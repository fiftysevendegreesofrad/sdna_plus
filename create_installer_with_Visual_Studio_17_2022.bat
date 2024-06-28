setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%
set CONFIG=Release

cmake -G "Visual Studio 17 2022" ^
      -A Win32 ^
      -B %THIS_FILE_DIR%\build_output_cmake_Win32 ^
      -S %SRC_DIR% ^
      -D USE_ZIG=OFF && ^
      -D BUNDLE_PYSHP=ON && ^
cmake --build %THIS_FILE_DIR%\build_output_cmake_Win32 --config %CONFIG% && ^
cmake -G "Visual Studio 17 2022" ^
      -A x64 ^
      -B %THIS_FILE_DIR%\build_output_cmake_x64 ^
      -S %SRC_DIR% ^
      -D USE_ZIG=OFF && ^
      -D BUNDLE_PYSHP=ON && ^
cmake --build %THIS_FILE_DIR%\build_output_cmake_x64 --config %CONFIG% && ^
AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .

@REM python -m pip install -r %THIS_FILE_DIR%\requirements\base.txt -r %THIS_FILE_DIR%\requirements\R.txt --target %THIS_FILE_DIR%\output\%CONFIG% && ^
