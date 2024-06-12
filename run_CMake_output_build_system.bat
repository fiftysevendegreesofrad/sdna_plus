setlocal
@REM BUILD_DIR Must be set externally, 
@REM e.g. by the required call beforehand to
@REM .\configure_for_zig.bat

if [%~1]==[] (
    set CONFIG="Release"
) else (
    set CONFIG=%~1
)

cmake --build %BUILD_DIR% --config %CONFIG%

