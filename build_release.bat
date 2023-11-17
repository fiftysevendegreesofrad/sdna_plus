call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" amd64

@REM c:\windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe build_installer.proj /t:rebuild /p:Configuration=release
"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" build_installer.proj /t:rebuild /p:Configuration=release

pause