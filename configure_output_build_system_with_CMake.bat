
set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


if [%~1]==[] (
    set PLATFORM=x64
) else (
    set PLATFORM=%~1
)

set BUILD_DIR=%THIS_FILE_DIR%\build_output_cmake_%PLATFORM%

cmake -B %BUILD_DIR% -S %SRC_DIR% -A %PLATFORM%