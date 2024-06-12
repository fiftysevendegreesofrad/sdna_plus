setlocal

if [%~1]==[] (
    set GENERATOR="Visual Studio 17 2022"
) else (
    set GENERATOR=%~1
)


if [%~2]==[] (
    set USE_ZIG=OFF
) else (
    set USE_ZIG=%~2
)

.\configure_output_build_system_with_CMake.bat Win32 "%GENERATOR%" %USE_ZIG% && ^
.\run_CMake_output_build_system.bat Release && ^
.\configure_output_build_system_with_CMake.bat x64 "%GENERATOR%" %USE_ZIG% && ^
.\run_CMake_output_build_system.bat Release && ^
AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .