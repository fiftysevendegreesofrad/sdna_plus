cmake_minimum_required(VERSION 3.26)

set(CMAKE_SYSTEM_VERSION 10.0 CACHE STRING "" FORCE)
# (i.e. Windows 10)

# I'm not sure how to set CMAKE_TOOLCHAIN_FILE in CMakePresets.json as recommended here:
# https://learn.microsoft.com/en-gb/vcpkg/users/buildsystems/cmake-integration#cmake_toolchain_file
set(CMAKE_TOOLCHAIN_FILE
 "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
 )

set(VCPKG_MANIFEST_DIR ${CMAKE_SOURCE_DIR})

set(PROJECT_NAME sdna_output)

project(${PROJECT_NAME})


if (${CMAKE_GENERATOR_PLATFORM} STREQUAL "x64")
    set(Bin_sub_dir 
        "/x64"
    )
else()
    set(Bin_sub_dir 
        ""
    )
endif()



message("Bin_sub_dir: ${Bin_sub_dir}")

add_subdirectory("sDNA/sdna_vs2008")


add_custom_target(${PROJECT_NAME} ALL)

add_dependencies(${PROJECT_NAME} "sdna_vs2008")

set(DLLs
    "sdna_vs2008.dll"
    "geos_c.dll"
)

set(Scripts
    "arcscripts/sDNA_ArcGIS_extra_tools.tbx"
    "arcscripts/runcalculation.py"
    "arcscripts/sDNA.pyt"
    "arcscripts/sDNAUISpec.py"
    "arcscripts/commandline_integral_prepare.py"
    "arcscripts/arc_utils.py"
    "arcscripts/sdna_environment.py"
    "arcscripts/sdnapy.py"
    "arcscripts/shapefile.py"
    "arcscripts/arc_import_itn.py"
    "arcscripts/arc_matchsymbologyranges.py"
    "arcscripts/sdnaregutilities.py"
    "arcscripts/boxcox.R"
    "arcscripts/boxtidwell.R"
    "arcscripts/regularizedregression.R"
    "arcscripts/runsdnacommand.py"
    "arcscripts/sdnaexception.py"
)
source_group("Scripts" FILES ${Scripts})

set(ScriptsBin
    "arcscripts/bin/_parentdir.py"
    "arcscripts/bin/README.txt"
    "arcscripts/bin/sdnaintegral.py"
    "arcscripts/bin/sdnaprepare.py"
    "arcscripts/bin/sdnalearn.py"
    "arcscripts/bin/sdnapredict.py"
)
source_group("ScriptsBin" FILES ${ScriptsBin})

set(InstallerBits
    "installerbits/license.rtf"
)
source_group("InstallerBits" FILES ${InstallerBits})



add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND echo "Making: ${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>${Bin_sub_dir}"   
)
add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>${Bin_sub_dir}"   
)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>/bin"   
)

foreach(dll ${DLLs})
    add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy "${PROJECT_BINARY_DIR}/sDNA/sdna_vs2008/$<CONFIG>/${dll}" "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>${Bin_sub_dir}/"
        DEPENDS "${PROJECT_BINARY_DIR}/sDNA/sdna_vs2008/$<CONFIG>/${dll}"
    )
endforeach()

foreach(script ${Scripts})
    add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_SOURCE_DIR}/${script}" "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>/"   
    )
endforeach()


foreach(script ${ScriptsBin})
    add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_SOURCE_DIR}/${script}" "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>/bin/"
    )
endforeach()

foreach(installer_bit ${InstallerBits})
    add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_SOURCE_DIR}/${installer_bit}" "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>/"
    )
endforeach()

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory_if_different "${CMAKE_CURRENT_SOURCE_DIR}/arcscripts/rportable" "${CMAKE_CURRENT_SOURCE_DIR}/output/$<CONFIG>/rportable"
)


# if (WIN32)

    # find_program(
    #     AdvancedInstaller
    #     "AdvancedInstaller.com"
    #     PATHS "C:/Program Files (x86)/Caphyon/Advanced Installer 21.7.1/bin/x86"
    #     REQUIRED
    #     )

    # message("Found: ${AdvancedInstaller}")


# endif()