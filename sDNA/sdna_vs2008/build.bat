@echo off
set THIS_FILE_DIR=%~dp0
set BUILD_DIR=%THIS_FILE_DIR%\..\..\build_cmake
cmake --build %BUILD_DIR%