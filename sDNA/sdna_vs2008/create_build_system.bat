@echo off
set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%
set BUILD_DIR=%THIS_FILE_DIR%\..\..\build_cmake
mkdir %BUILD_DIR%
cmake -B %BUILD_DIR% -S %SRC_DIR%