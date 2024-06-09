setlocal

if [%~1]==[] (
    set GENERATOR="Visual Studio 17 2022"
) else (
    set GENERATOR=%~1
)

.\configure_output_build_system_with_CMake.bat Win32 %GENERATOR% && ^
.\run_CMake_output_build_system.bat && ^
.\configure_output_build_system_with_CMake.bat x64 %GENERATOR% && ^
.\run_CMake_output_build_system.bat && ^
AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .