@REM xcopy drop x86\ /E
xcopy drop x64\ /E

rem path must be set to include c:\Program Files\Microsoft Visual Studio 9.0\VC\bin

cd x64
call autogen.bat

call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\Vcvarsall.bat" amd64

nmake /f makefile.vc MSVC_VER=1500
cd ..

@REM cd x86
@REM call autogen.bat

@REM call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\Vcvarsall.bat" x86

@REM nmake /f makefile.vc MSVC_VER=1500
@REM cd ..

