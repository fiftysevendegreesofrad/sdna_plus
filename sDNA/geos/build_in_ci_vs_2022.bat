xcopy drop x86\ /E
xcopy drop x64\ /E

rem path must be set to include "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\bin"
REM as it had to include c:\Program Files\Microsoft Visual Studio 9.0\VC\bin for build.bat?
set VCVARSALL="C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Auxiliary\Build\vcvarsall.bat"

cd x64
call autogen.bat

call %VCVARSALL% amd64

nmake /f makefile.vc MSVC_VER=1500
cd ..

cd x86
call autogen.bat

call %VCVARSALL% x86

nmake /f makefile.vc MSVC_VER=1500
cd ..