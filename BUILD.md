## Overview

### Cross platform

* The MuParser .cpp files are as they are in the original repo.  
* They are dynamically prefixed with `#include stdafx.h\n` within a custom prebuild step
within the .vcxproj.
* The installer from (`installerbits\advanced\sdna.aip` using Cahyon's AdvancedInstaller) contains both Win32 and x64 .dlls
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
* ` sudo apt purge --auto-remove cmake`
* `wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null`
* `sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ jammy main'`
* `sudo apt update`
* `sudo apt-get install curl zip unzip tar g++ python-is-python3 cmake ninja-build `
* `git clone --depth=1 http://www.github.com/Microsoft/vcpkg`
* `cd vcpkg`
* `./bootstrap-vcpkg.sh`
* `cd ..`
* `export VCPKG_ROOT = /path/to/vcpkg`
* `git clone --depth=1 --branch=Cross_Platform  http://www.github.com/fiftysevendegreesofrad/sdna_plus`
* `cd sDNA_plus`
* `which ninja`
* `export CMAKE_MAKE_PROGRAM=/usr/bin/path/to/ninja`
* `cmake -G "Ninja Multi-Config" -D USE_ZIG=OFF  -B build_linux -S .`
May also require `sudo` or `-D VCPKG_ROOT=/path/to/vcpkg`
* `cmake --build build_linux --config=Release`
Run a test
* `export sdnadll=/root/sdna_plus/output/Release/x64/sdna_vs2008.so`
* `cd sDNA/sdna_vs2008/tests`
* `python prepare_test_new.py`
## Compilation notes.
~~tl;dr  A Breaking change to sDNA, or maintaining two similar branches 
should be considered.  

Minor changes to the source of an idiosyncratic
 static dependency (MuParser) in the sdna_plus repo, to allow 
builds via CMake and Visual Studio (and possibly gcc in future), break 
builds via the existing .sln and .vcxproj, and vice versa.~~  

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

```
  D:\a\sdna_plus\sdna_plus\sdna\muparser\drop\src\muParser.cpp(387,1): error C1010: unexpected end of file while looking for precompiled header. Did you forget to add '#include "stdafx.h"' to your source? [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
  D:\a\sdna_plus\sdna_plus\sdna\muparser\drop\src\muParserBase.cpp(1775,1): error C1010: unexpected end of file while looking for precompiled header. Did you forget to add '#include "stdafx.h"' to your source? [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
  D:\a\sdna_plus\sdna_plus\sdna\muparser\drop\src\muParserBytecode.cpp(586,1): error C1010: unexpected end of file while looking for precompiled header. Did you forget to add '#include "stdafx.h"' to your source? [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
  D:\a\sdna_plus\sdna_plus\sdna\muparser\drop\src\muParserCallback.cpp(463,1): error C1010: unexpected end of file while looking for precompiled header. Did you forget to add '#include "stdafx.h"' to your source? [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
  D:\a\sdna_plus\sdna_plus\sdna\muparser\drop\src\muParserError.cpp(337,1): error C1010: unexpected end of file while looking for precompiled header. Did you forget to add '#include "stdafx.h"' to your source? [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
  D:\a\sdna_plus\sdna_plus\sdna\muparser\drop\src\muParserTokenReader.cpp(956,1): error C1010: unexpected end of file while looking for precompiled header. Did you forget to add '#include "stdafx.h"' to your source? [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
```

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

 ```
 D:\a\sdna_plus\sdna_plus\sDNA\muparser\drop\src\muParser.cpp(26,10): error C1083: Cannot open include file: 'stdafx.h': No such file or directory [D:\a\sdna_plus\sdna_plus\build_cmake\sdna_vs2008.vcxproj]
  (compiling source file '../sDNA/muparser/drop/src/muParser.cpp')
  
D:\a\sdna_plus\sdna_plus\sDNA\muparser\drop\src\muParserBase.cpp(25,10): error C1083: Cannot open include file: 'stdafx.h': No such file or directory [D:\a\sdna_plus\sdna_plus\build_cmake\sdna_vs2008.vcxproj]
  (compiling source file '../sDNA/muparser/drop/src/muParserBase.cpp')
  
D:\a\sdna_plus\sdna_plus\sDNA\muparser\drop\src\muParserBytecode.cpp(25,10): error C1083: Cannot open include file: 'stdafx.h': No such file or directory [D:\a\sdna_plus\sdna_plus\build_cmake\sdna_vs2008.vcxproj]
  (compiling source file '../sDNA/muparser/drop/src/muParserBytecode.cpp')
  
D:\a\sdna_plus\sdna_plus\sDNA\muparser\drop\src\muParserCallback.cpp(25,10): error C1083: Cannot open include file: 'stdafx.h': No such file or directory [D:\a\sdna_plus\sdna_plus\build_cmake\sdna_vs2008.vcxproj]
  (compiling source file '../sDNA/muparser/drop/src/muParserCallback.cpp')
  
D:\a\sdna_plus\sdna_plus\sDNA\muparser\drop\src\muParserError.cpp(25,10): error C1083: Cannot open include file: 'stdafx.h': No such file or directory [D:\a\sdna_plus\sdna_plus\build_cmake\sdna_vs2008.vcxproj]
  (compiling source file '../sDNA/muparser/drop/src/muParserError.cpp')
  
D:\a\sdna_plus\sdna_plus\sDNA\muparser\drop\src\muParserTokenReader.cpp(25,10): error C1083: Cannot open include file: 'stdafx.h': No such file or directory [D:\a\sdna_plus\sdna_plus\build_cmake\sdna_vs2008.vcxproj]
  (compiling source file '../sDNA/muparser/drop/src/muParserTokenReader.cpp')
 ```
 9) Using CMake allows the MuParser source to be restored closer to its original state,
 (except for 4) which I have not been able to avoid - the other `#define MUP_BASETYPE` in 
 stdafx.h does not seem to 
 have any effect).  
 10) However a form of the source code in MuParser that can be compiled by both CMake, and
 the sdna_vs2008.vcxproj has not yet been find

### Compiling sDNA with `zig c++`
`zig c++` is claimed to be a drop in compiler replacement for MSVC.
 It is based on LLVM (and is reportedly like Clang with better defaults).

 * Numerous (hopefully minor) changes to the sDNA C++ code have been made on this branch to facilitate compilation using `zig c++`, but unfortunately these caused a regression in one of the tests, using the existing MSVC build chain (after including the `#include stdafx.h`s in MuParser).  The dll produced using `zig C++` has not yet been tested at all
 * The sDNA CMakelists.txt is used to set up Zig and Ninja, by pulling in a modified version of Duncan Ogilvie's example CMake Toolchain for Zig:  https://github.com/mrexodia/zig-cross (in `zigcross-cmake`)
 * Previous mainstream releases of sDNA have been using MSVC header files to access the Windows API, to dynamically link to geos_c.dll.  By default `zig c++` targets Windows using the header files from [MinGW-w64](https://www.mingw-w64.org/) instead of Microsoft's.
 * A Win32 dll has not been produced yet (and therefore neither has a .msi instealler, just an output directory).  Ninja takes the arch from the env, not during config (i.e. not from CMake).  When running MSVC builds via Ninja, this is possibly as simple to fix as running vcvarsall.bat Win32 before hand.  Equivalent steps that will work with `zig c++` need to be found.

### Compiling sDNA with `zig c++`
`zig c++` is claimed to be a drop in compiler replacement for MSVC.
 It is based on LLVM (and is reportedly like Clang with better defaults).

 * Numerous (hopefully minor) changes to the sDNA C++ code have been made on this branch to facilitate compilation using `zig c++`, but unfortunately these caused a regression in one of the tests, using the existing MSVC build chain (after including the `#include stdafx.h`s in MuParser).  The dll produced using `zig C++` has not yet been tested at all
 * The sDNA CMakelists.txt is used to set up Zig and Ninja, by pulling in a modified version of Duncan Ogilvie's example CMake Toolchain for Zig:  https://github.com/mrexodia/zig-cross (in `zigcross-cmake`)
 * Previous mainstream releases of sDNA have been using MSVC header files to access the Windows API, to dynamically link to geos_c.dll.  By default `zig c++` targets Windows using the header files from [MinGW-w64](https://www.mingw-w64.org/) instead of Microsoft's.
 * A Win32 dll has not been produced yet (and therefore neither has a .msi instealler, just an output directory).  Ninja takes the arch from the env, not during config (i.e. not from CMake).  When running MSVC builds via Ninja, this is possibly as simple to fix as running vcvarsall.bat Win32 before hand.  Equivalent steps that will work with `zig c++` need to be found.


### Attempted Solutions 
 (to allow both compilation methods via the same branch/code base).
 i) Preprocessor macros (`#ifndef`) to conditionally `#include stdafx.h` based on 
 a directive in CMakeLists.txt will not work as Visual Studio ignores them due to 2).
 ii) Compiling without a pre-compiled header at all (as commonly suggested online).  All 
 source code files compile to object code, but Linker errors regarding MuParser are 
 encountered.  Some sort of second pass is needed to successfully link the .dll, and if possible
 this might as well be the normal compiler pass after creating the pre-compiled header.

 The error below was produced using an adjusted sdna_vs2008.vcxproj with the pre-compiled 
 header turned off.  But if compiling with CMake very similar errors in the same files are 
 produced if force including the pre-compiled header is skipped only for the 
 MuParser files (without #include stdafx.h) (by adding 
 `set_source_files_properties(${MuParser} PROPERTIES SKIP_PRECOMPILE_HEADERS 1)` in CMakeLists.txt).

```
x64\Release\muParserBytecode.obj
  x64\Release\muParserCallback.obj
  x64\Release\muParserError.obj
  x64\Release\muParserTokenReader.obj
  x64\Release\net.obj
  x64\Release\prepareoperations.obj
  x64\Release\random.obj
  x64\Release\sdna_geometry_collections.obj
  x64\Release\sDNACalculationFactory.obj
  x64\Release\stdafx.obj
  x64\Release\unit_tests.obj
     Creating library D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\x64\Release\sdna_vs2008.lib and object D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\x64\Release\sdna_vs2008.exp
metricevaluator.obj : error LNK2001: unresolved external symbol "private: void __cdecl mu::ParserBase::AddCallback(class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const &,class mu::ParserCallback const &,class std::map<class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> >,class mu::ParserCallback,struct std::less<class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > >,class std::allocator<struct std::pair<class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const ,class mu::ParserCallback> > > &,char const *)" (?AddCallback@ParserBase@mu@@AEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@AEBVParserCallback@2@AEAV?$map@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@VParserCallback@mu@@U?$less@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@V?$allocator@U?$pair@$$CBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@VParserCallback@mu@@@std@@@2@@4@PEBD@Z) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: char const * __cdecl mu::ParserBase::ValidNameChars(void)const " (?ValidNameChars@ParserBase@mu@@QEBAPEBDXZ) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: void __cdecl mu::ParserBase::DefineVar(class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const &,float *)" (?DefineVar@ParserBase@mu@@QEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@PEAM@Z) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: void __cdecl mu::ParserBase::DefineConst(class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const &,float)" (?DefineConst@ParserBase@mu@@QEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@M@Z) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: void __cdecl mu::ParserBase::SetVarFactory(float * (__cdecl*)(char const *,void *),void *)" (?SetVarFactory@ParserBase@mu@@QEAAXP6APEAMPEBDPEAX@Z1@Z) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: void __cdecl mu::ParserBase::SetExpr(class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const &)" (?SetExpr@ParserBase@mu@@QEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const & __cdecl mu::ParserError::GetMsg(void)const " (?GetMsg@ParserError@mu@@QEBAAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@XZ) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
metricevaluator.obj : error LNK2001: unresolved external symbol "public: __cdecl mu::ParserError::ParserError(char const *,int,class std::basic_string<char,struct std::char_traits<char>,class std::allocator<char> > const &)" (??0ParserError@mu@@QEAA@PEBDHAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z) [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\x64\Release\sdna_vs2008.dll : fatal error LNK1120: 8 unresolved externals [D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj]
Done Building Project "D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.vcxproj" (Rebuild target(s)) -- FAILED.
Done Building Project "D:\a\sdna_plus\sdna_plus\sdna\sdna_vs2008\sdna_vs2008.sln" (Rebuild target(s)) -- FAILED.
Done Building Project "D:\a\sdna_plus\sdna_plus\build_output.proj" (Rebuild target(s)) -- FAILED.
Done Building Project "D:\a\sdna_plus\sdna_plus\build_installer.proj" (rebuild target(s)) -- FAILED.
Build FAILED.
```

iii)  Turning off optimisation and linker options.  No avail.
iv)   Creating a fresh .vcxproj in VS 2022 using the wizard.  Other errors encountered.

### Other possible solutions (not yet tried)

i) Dynamically change MuParser's source code in a custom pre-build step (e.g. Python 
script or sed command) similar to `sDNA\sdna_vs2008\version_generated.h.creator.py`.  

ii) Figure out how to override MuParser's `#define MUP_BASETYPE` by fixing the `#define` in
`stdafx.h`.

iii) Refactor MuParser into vcpkg like Boost.  It's unclear if a pre-build step
can be applied to dependencies built by vcpkg (i.e. to `#define MUP_BASETYPE float`).

iv) Fork MuParser and refactor it to use Generics (instead of having users
change `#define MUP_BASETYPE` to avoid `double`s).  Elegant, but increases maintenance
burden, and a lot of work.