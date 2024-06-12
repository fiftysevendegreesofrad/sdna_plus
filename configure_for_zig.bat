@echo off
@REM Don't use setlocal.  Subsequent calls of 
@REM ./run_CMake_output_build_system.bat use
@REM the value of %BUILD_DIR% set below.

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


set BUILD_DIR=%THIS_FILE_DIR%\build_output_cmake_zig

cmake -G "Ninja Multi-Config" ^
      -B %BUILD_DIR% ^
      -S %SRC_DIR%