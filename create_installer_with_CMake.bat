setlocal

if [%~1]==[] (
    @REM set GENERATOR="Visual Studio 17 2022"
    set GENERATOR="Ninja Multi-Config"
) else (
    set GENERATOR=%~1
)

.\configure_output_build_system_with_CMake.bat Win32 %GENERATOR% && ^
.\run_CMake_output_build_system.bat Release && ^
.\configure_output_build_system_with_CMake.bat x64 %GENERATOR% && ^
.\run_CMake_output_build_system.bat Release && ^
AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .