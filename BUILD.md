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
##### Ubuntu 22.04 (Jammy)
Kitware haven't got a repo for Noble (24.04) yet, so 22.04 is needed for now.
[Upgrade CMake to 3.29](https://askubuntu.com/a/1157132)
Working directory assumed to be `/root`
* `sudo apt purge --auto-remove cmake`
* `wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null`
* `sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ jammy main'`
* `sudo apt update`
* `sudo apt-get install curl zip unzip tar g++ python-is-python3 python3-pip cmake ninja-build `
* `git clone --depth=1 http://www.github.com/Microsoft/vcpkg`
* `cd vcpkg`
* `./bootstrap-vcpkg.sh`
* `cd ..`
* `git clone --depth=1 --branch=Cross_platform  http://www.github.com/fiftysevendegreesofrad/sdna_plus`
Download GEOS 3.3.5 and compile it locally (so that it can link to your available version of glibc, instead of whichever one was in the build environment I used).  `.github\workflows\build_geos.yml` can be used in a Github Action Ubuntu runner.
* `curl -OL http://download.osgeo.org/geos/geos-3.3.5.tar.bz2`
* `tar xfj geos-3.3.5.tar.bz2`
* `cd geos-3.3.5`
* `cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/root/build_geos/_installed -DBUILD_SHARED_LIBS=ON -DBUILD_DOCUMENTATION=OFF -DBUILD_TESTING=OFF -G Ninja -B /root/build_geos -S .`
* `cmake --build /root/build_geos`
* `cp /root/build_geos/lib/libgeos_c.so /root/sdna_plus/sDNA/geos/x64/src`
* `cd sdna_plus`
* `which ninja`
* `VCPKG_INSTALLATION_ROOT=/root/vcpkg cmake -G "Ninja Multi-Config" -D USE_ZIG=OFF -D CMAKE_MAKE_PROGRAM=/usr/bin/ninja -B build_linux -S .`
* `cmake --build build_linux --config=Release`
Install user-land dependencies (R).
* `sudo apt-get install r-cran-optparse r-cran-sjstats`
Run a smoke test
* `export sdnadll=/root/sdna_plus/output/Release/x64/sdna_vs2008.so`
* `cd sDNA/sdna_vs2008/tests`
* `python prepare_test_new.py`
Run all regression tests:
If this isn't a throw away env, make a venv and activate it.
* `python -m pip install pytest`
* `cd /root/sdna_plus/sDNA/sdna_vs2008/tests/pytest`
* `pytest`
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




