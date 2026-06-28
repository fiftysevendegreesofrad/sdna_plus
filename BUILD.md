## Overview

### Cross platform

* The MuParser .cpp files are as they are in the original repo.  
* They are dynamically prefixed with `#include stdafx.h\n` within a custom prebuild step
within the .vcxproj.
* The installer from (`installerbits\advanced\sdna.aip` using Caphyon's AdvancedInstaller) contains both Win32 and x64 .dlls
* `zig c++` on Windows (repackaged Clang) does not support Win32, so can only be used to
produce an x64 output installation.
* All an installer needs to be for Zig/Windows and Linux is a zip file of the output directory.
* Compilation is achieved 5 different ways, but run time errors will be enountered on 3 of these builds.
* The tests can run on all of them (uncomment the job in the workflow) but currently are only passed by the 2 Visual Studio builds (CMake and MSBuild).
* Work needs to be done to dynamically link to the Geos DLLs and .so (and to provide the latter) on both
the Zig for Windows build (entirely optional) and the Linux builds.

#### Building locally on Linux 

##### Quick build (recommended)

On any modern Ubuntu/Debian system (20.04+):

```bash
# Install prerequisites (one-time, needs ~480 MB space)
sudo apt update
sudo apt install cmake make g++ libboost-dev python3 -y

# Clone and build
git clone --depth=1 --branch=Cross_platform https://github.com/fiftysevendegreesofrad/sdna_plus
cd sdna_plus
sudo bash build_linux.sh
```

This produces `output/Release/x64/sdna_vs2008.so` with **OpenMP multi-threading** enabled,
and bundles `libgeos_c.so` for spatial operations. All dependencies come from system packages —
no vcpkg required.

The script works on Ubuntu 20.04 through 26.04, and Debian 11+.
Tested with GCC 10–15 and Boost 1.71–1.90.

To use with vcpkg for pinned Boost 1.83 (matching CI exactly):
```bash
git clone --depth=1 https://github.com/microsoft/vcpkg ~/vcpkg
cd ~/vcpkg && ./bootstrap-vcpkg.sh
cd path/to/sdna_plus
VCPKG_ROOT=~/vcpkg sudo bash build_linux.sh
```

##### Manual CMake build

If you prefer to run the steps individually:

```bash
sudo apt install cmake make g++ libboost-dev

# Create a stub vcpkg (or use real vcpkg)
mkdir -p /tmp/sdna_vcpkg_stub/scripts/buildsystems
echo 'set(VCPKG_MANIFEST_MODE OFF)' > /tmp/sdna_vcpkg_stub/scripts/buildsystems/vcpkg.cmake

# Configure and build
VCPKG_ROOT=/tmp/sdna_vcpkg_stub cmake -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release -DUSE_ZIG=OFF -DBUNDLE_PYSHP=OFF \
    -B build_linux -S .
cmake --build build_linux --parallel $(nproc)

# Copy outputs manually (post-build copy uses multi-config paths)
mkdir -p output/Release/x64 output/Release/bin
cp build_linux/sDNA/sdna_vs2008/sdna_vs2008.so output/Release/x64/
cp sDNA/geos/x64/src/libgeos_c.so output/Release/x64/
cp -r arcscripts/* output/Release/
cp -r arcscripts/bin/* output/Release/bin/
```

Install user-land dependencies (R, required for sDNA Learn/Predict):
```bash
sudo apt-get install r-cran-optparse r-cran-sjstats
```

Run a smoke test:
```bash
export SDNADLL=$(pwd)/output/Release/x64/sdna_vs2008.so
cd sDNA/sdna_vs2008/tests
python3 prepare_test_new.py
```
Run all regression tests:
If this isn't a throw away env, make a venv and activate it.
* `python -m pip install pytest`
* `cd /root/sdna_plus/sDNA/sdna_vs2008/tests/pytest`
* `pytest`
###### Building an sDNA Python Wheel (also on Ubuntu 22.04)
* `export VCPKG_INSTALLATION_ROOT=/root/vcpkg`
* `python -m venv venv`
* `. venv/bin/activate`
* `pip install build hatchling`
* `cd sdna_plus`
* `python -m build --no-isolation --wheel`
TODO:  For better compatibility across Linux distros, the above Ubuntu 22.04 steps need to 
be generalised to builds from source for
CMake 29 etc. if necessary, and wheels built on the many linux image `quay.io/pypa/manylinux1_x86_64` that
supports a GCC 4.8 version that was released 16 months after Geos 3.3.5.  See https://github.com/pypa/manylinux
https://gcc.gnu.org/news.html and https://github.com/libgeos/geos/blob/main/NEWS.md

## Compilation notes.
#### Dynamic changes to the source code when compiling with Visual Studio
The Python script `sDNA\sdna_vs2008\preppend_muparser_cpps_with_include_stdafx.h.py`
dynamically changes the static copy of the MuParser code. It is run in a custom pre-build 
step similar to `sDNA\sdna_vs2008\version_generated.h.creator.py`  
from `sDNA\sdna_vs2008\sdna_vs2008.vcxproj`.

This is because in order to compile code that will link to a pre-compiled 
header `stdafx.h` with Visual Studio, it must occur after an `#include stdafx.h` 
directive.  All lines before the first such directive are ignored by Visual Studio. 
CMake configures PCHs as "forced includes", for which there must be no `#include stdafx.h`s,
so the above "preppend_" Python script is not used in those builds. 
### Background
 0) The sDNA dll is compiled using Visual Studio, and a pre-compiled header (stdafx.h in sDNA).  
 1) Its source code follows the Visual Studio convention of making the 
first line of every file `#include stdafx.h`
 2) When using a pre-compiled header, on the second pass Visual Studio
(["the compiler ignores all preprocessor directives (including pragmas)"](https://learn.microsoft.com/en-us/cpp/build/creating-precompiled-header-files?view=msvc-170#source-file-consistency))
Possible other lines of code before the `#include stdafx.h` are ignored too.
 3) The sDNA source code repo includes static copies of dependencies (Muparser, AnyIterator and geos binaries (the geos source was included in sdna_open.  R-portable is shipped as data)).
 4) Muparser requires a base type to be set in its definition file (`#define MUP_BASETYPE float` in sDNA\muparser\drop\include\muParserDef.h)
 5) Compilation errors are raised in sDNA when MuParser does not `#include stdafx.h` 
    so sDNA's copy of Muparser was adjusted to include these lines (in 6 of the 
    sDNA\muparser\drop\src\muParser*.cpp) to produce a successful a build.
 6) Cross platform C++ projects, instead of requiring `#include stdafx.h` in every file, may 
    instead have the compiler Force Include the precompiled header (`\FI` option).
 7) I have not worked out how to easily do so via the Visual Studio GUI, but CMake 
 can generate a .vcxproj that achieves Force Inclusion of a precompiled header 
 successfully, however:
 8) Although the Visual Studio compiler is happy with both `#include stdafx.h` in all of sDNA's 
 own source files, whilst also Force Including it, an error is raised at those lines in MuParser due 
 to a missing file (the CMake VS generator compiles the PCH to "build_cmake\sdna_vs2008.dir\{Configuration}\cmake_pch.pch"):
 9) Using CMake allows the MuParser source to be restored closer to its original state,
 (except for 4) which I have not been able to avoid - the other `#define MUP_BASETYPE` in 
 stdafx.h does not seem to 
 have any effect.  
 10) However a form of the source code in MuParser that can be compiled by both CMake, and
 the sdna_vs2008.vcxproj has not yet been find




