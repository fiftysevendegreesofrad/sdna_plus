setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


cmake -G "Ninja" ^
      -B %THIS_FILE_DIR%\build_output_cmake_Zig ^
      -S %SRC_DIR% ^
      -D USE_ZIG=ON && ^
cmake --build %BUILD_DIR% --config Release
