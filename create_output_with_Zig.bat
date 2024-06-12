setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


cmake -G "Ninja Multi-Config" ^
      -B %THIS_FILE_DIR%\build_output_cmake_Zig ^
      -S %SRC_DIR% ^
      -D USE_ZIG=ON && ^
cmake --build %THIS_FILE_DIR%\build_output_cmake_Zig --config Release
