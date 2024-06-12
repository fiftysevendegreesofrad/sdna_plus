setlocal
@REM BUILD_DIR Must be set externally, 
@REM e.g. by the required call beforehand to
@REM .\configure_for_zig.bat

if [%~1]==[] (
    set CONFIG="Release"
) else (
    set CONFIG=%~1
)

@REM echo Build_Dir %BUILD_DIR%

@REM echo Config %CONFIG%

cmake --build %BUILD_DIR% --config %CONFIG%

