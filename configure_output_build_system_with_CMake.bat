
set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


if [%~1]==[] (
    set PLATFORM=x64
) else (
    set PLATFORM=%~1
)

if ["%~2"]==[""] (
    set GENERATOR="Visual Studio 17 2022"
) else (
    set GENERATOR=%~2
)


if [%~3]==[] (
    set USE_ZIG=OFF
) else (
    set USE_ZIG=%~3
)

echo %PLATFORM%

echo %GENERATOR%

echo %USE_ZIG%

set BUILD_DIR=%THIS_FILE_DIR%\build_output_cmake_%PLATFORM%

cmake -G "%GENERATOR%" ^
      -B %BUILD_DIR% ^
      -S %SRC_DIR% ^
      -D USE_ZIG=%USE_ZIG%