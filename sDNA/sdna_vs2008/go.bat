setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%

cmake -G "Visual Studio 17 2022" ^
      -A x64 ^
      -B %THIS_FILE_DIR%\..\..\build_output_cmake_x64 ^
      -S %SRC_DIR% ^
cmake --build %THIS_FILE_DIR%\build_output_cmake_x64 --config Release && ^