@echo off
if [%1%]==[] (
 echo No platform (e.g. processor architecture^) specified
 goto echo_supported_args_and_exit
)

if not %1==x86 (
   if not %1==x64 (
    echo Arg: %1 not supported.
	goto echo_supported_args_and_exit
   )
)

set CWD=%cd%

set BUILD_DIR=%~dp0\%1%\src
mkdir %BUILD_DIR%

cd %BUILD_DIR%

rem https://web.archive.org/web/20120715050247/http://trac.osgeo.org/geos/wiki/BuildingOnWindowsWithCMake

cmake -G "Visual Studio 9 2008" ..\..\drop || goto error

cd %CWD%

echo CMake successfully built geos.sln!  
"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\Vcvarsall.bat" %1
msbuild /p:ContinueOnError=false %BUILD_DIR%\geos.sln || goto error

exit /b 0

:error
echo echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:echo_supported_args_and_exit
echo Supported args: (x86, x64^)
exit /b 1