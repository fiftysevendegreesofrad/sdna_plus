setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%


@REM cmake -G "Visual Studio 17 2022" ^
@REM       -A Win32 ^
@REM       -B %THIS_FILE_DIR%\build_output_cmake_Win32 ^
@REM       -S %SRC_DIR% ^
@REM       -D USE_ZIG=OFF && ^
@REM cmake --build %THIS_FILE_DIR%\build_output_cmake_Win32 --config Release && ^
cmake -G "Visual Studio 17 2022" ^
      -A x64 ^
      -B %THIS_FILE_DIR%\build_output_cmake_x64 ^
      -S %SRC_DIR% ^
      -D USE_ZIG=OFF && ^
cmake --build %THIS_FILE_DIR%\build_output_cmake_x64 --config Release
@REM  && ^
@REM AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
@REM python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .