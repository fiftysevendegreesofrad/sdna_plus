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


#### Building an sDNA Python Wheel
* `export VCPKG_INSTALLATION_ROOT=/root/vcpkg`
* `python -m venv venv`
* `. venv/bin/activate`
* `pip install build hatchling`
* `cd sdna_plus`
* `python -m build --no-isolation --wheel`
TODO:  For better compatibility across Linux distros, the above Ubuntu 22.04 steps need to 
be generalised to builds from source for CMake 29 etc. if necessary, and wheels built on 
the many linux image `quay.io/pypa/manylinux1_x86_64` that
supports a GCC 4.8 version that was released 16 months after Geos 3.3.5.  See https://github.com/pypa/manylinux
https://gcc.gnu.org/news.html and https://github.com/libgeos/geos/blob/main/NEWS.md

#### Building locally on Linux 

#### Building with the operating system's Boost and other libraries

##### GLIBC
Note.  As with any dynamically linked libary, an error will occur if the resulting binaries are run 
on a distro with an older GLIBC, than the GLIBC on the system the sDNA build was compiled on, and linked against.
This route should not be used for the official binaries for release, that we will try to support.  It 
is for quickly producing personal customised unofficial versions of sDNA only.

##### Ubuntu 26.04
It is possible to build sDNA on Linux much quicker, by linking to the operating system's libraries 
(GLIBC and Boost), instead of installing vcpkg, and compiling the same pinned version of Boost
(1.83) as the main branch from source.  
If vcpkg is not available, the script `build_linux.sh` does this automatically.


#### Quick build (e.g. without vcpkg)
Tested on x64/x86 (not ARM yet), on Ubuntu 26.04, 24.04, and on Debian Trixie.  On 
Ubuntu 24.04 and other older distros, see note below about adding Kitware's repositories for CMake >= 3.29

```bash
sudo apt update
sudo apt install git cmake ninja-build g++ libboost-dev python3-venv -y

git clone --depth=1 --branch=Cross_platform https://github.com/fiftysevendegreesofrad/sdna_plus
cd sdna_plus
bash build_linux.sh
```

This produces sDNA in `./output/Release/x64`.  All dependencies come 
from system packages —no vcpkg required.

The script works on Ubuntu 24.04, 26.04, and Debian Trixie.
Tested with GCC 10–15 and Boost 1.71–1.90.


To use with vcpkg for pinned Boost 1.83 (as in our CI pipeline):
```bash
git clone --depth=1 https://github.com/microsoft/vcpkg ~/vcpkg
cd ~/vcpkg && ./bootstrap-vcpkg.sh
cd path/to/sdna_plus
VCPKG_ROOT=~/vcpkg bash build_linux.sh
```

##### Ubuntu 24.04

###### Installing CMake on Debian based distros, if >= 3.29 unavailable in default apt repos
Follow [the instructions](https://apt.kitware.com/) to configure your package manager (apt)
to download directly from Kitware's CMake apt repository.  E.g. on Ubuntu 24.04:

```bash
sudo apt update &&
sudo apt install -y ca-certificates gpg wget &&
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null &&
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ noble main' | tee /etc/apt/sources.list.d/kitware.list &&
sudo apt update
```

#### Standard build.

##### Ubuntu 22.04 (Jammy)
Kitware haven't got a repo for Noble (24.04) yet, so 22.04 is needed for now.
[Upgrade CMake to 3.29](https://askubuntu.com/a/1157132)
Working directory assumed to be `/root`
* `sudo apt purge --auto-remove cmake`
* `wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null`
* `sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ jammy main'`
* `sudo apt update`
* `sudo apt-get install curl zip unzip tar g++ python-is-python3 python3-venv cmake ninja-build `
* `git clone --depth=1 http://www.github.com/Microsoft/vcpkg`
* `cd vcpkg`
* `./bootstrap-vcpkg.sh`
On ARM:
* `export VCPKG_FORCE_SYSTEM_BINARIES=1`
* `cd ..`
* `git clone --depth=1 --branch=Cross_platform  http://www.github.com/fiftysevendegreesofrad/sdna_plus`
Download GEOS 3.3.5 and compile it locally (so that it can link to your available version of glibc, instead of whichever one was in the build environment I used).  `.github\workflows\build_geos.yml` can be used in a Github Action Ubuntu runner.
* `curl -OL http://download.osgeo.org/geos/geos-3.3.5.tar.bz2`
* `tar xfj geos-3.3.5.tar.bz2`
* `cd geos-3.3.5`
* `cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/root/build_geos/_installed -DBUILD_SHARED_LIBS=ON -DBUILD_DOCUMENTATION=OFF -DBUILD_TESTING=OFF -G Ninja -B /root/build_geos -S .`
* `cmake --build /root/build_geos`
* `cp /root/build_geos/lib/libgeos_c.so /root/sdna_plus/sDNA/geos/x64/src`
Then pick one of the following package options
###### Simple output dir 
The `output/Config` dir is automatically zipped if it was built in one of the Github Actions workflows, 
e.g. `.github\workflows\smoke_test_gcc.yml`
* `cd sdna_plus`
* `VCPKG_INSTALLATION_ROOT=/root/vcpkg cmake -G "Ninja Multi-Config" -D USE_ZIG=OFF -D CMAKE_MAKE_PROGRAM=/usr/bin/ninja -D BUNDLE_PYSHP=ON -B build_linux -S .`
* `cmake --build build_linux --config=Release`
Install user-land dependencies (R).
* `sudo apt-get install r-cran-optparse r-cran-sjstats`
Run a smoke test
* `export sdnadll=/root/sdna_plus/output/Release/x64/sdna_vs2008.so`
* `cd sDNA/sdna_vs2008/tests`
* `python prepare_test_new.py`


#### Install user-land dependencies.
If using sDNA Learn/Predict, Numpy and R are needed:
```bash
python3 -m pip install -r requirements/learn-predict.txt
sudo apt-get install r-cran-optparse r-cran-sjstats # Warning!  Can need 3.5GB
```

Run a smoke test:
```bash
export sdnadll=$(pwd)/output/Release/x64/sdna_vs2008.so
cd sDNA/sdna_vs2008/tests
python3 prepare_test_new.py
```
Run all regression tests:
If this isn't a throw away env, make a venv and activate it.
* `python -m pip install pytest`
* `cd /root/sdna_plus/sDNA/sdna_vs2008/tests/pytest`
* `DONT_TEST_N_LINK_SUBSYSTEMS_ORDER=1 && ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT=1 && pytest`




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




