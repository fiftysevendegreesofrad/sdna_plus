setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


cmake -G "Visual Studio 17 2022" ^
      -A Win32 ^
      -B %THIS_FILE_DIR%\build_output_cmake_Win32 ^
      -S %SRC_DIR% ^
      -D USE_ZIG=OFF && ^
cmake --build %BUILD_DIR% --config Release && ^
cmake -G "Visual Studio 17 2022" ^
      -A x64 ^
      -B %THIS_FILE_DIR%\build_output_cmake_x64 ^
      -S %SRC_DIR% ^
      -D USE_ZIG=OFF && ^
cmake --build %BUILD_DIR% --config Release && ^
AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .