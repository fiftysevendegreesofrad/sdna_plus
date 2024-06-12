
@REM BUILD_DIR Must be set externally, e.g. by .\configure_output_build_system_with_CMake.bat

cmake --build %BUILD_DIR% --config Release

@REM AdvancedInstaller.com /build installerbits\advanced\sdna.aip
@REM "C:/Program Files (x86)/Caphyon/Advanced Installer 21.7.1/bin/x86/AdvancedInstaller.com" /build installerbits\advanced\sdna.aip

@REM python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .