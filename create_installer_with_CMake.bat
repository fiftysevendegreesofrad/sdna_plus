.\configure_output_build_system_with_CMake.bat Win32 && ^
.\run_CMake_output_build_system_and_create_installer.bat && ^
.\configure_output_build_system_with_CMake.bat x64 && ^
.\run_CMake_output_build_system_and_create_installer.bat && ^
AdvancedInstaller.com /build installerbits\advanced\sdna.aip && ^
python -u installerbits\rename_version.py installerbits/advanced/output/sdna_setup.msi .