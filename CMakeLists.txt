cmake_minimum_required(VERSION 3.26)

set(CMAKE_SYSTEM_VERSION 10.0 CACHE STRING "" FORCE)
# (i.e. Windows 10)

set(PROJECT_NAME sdna_output)

project(${PROJECT_NAME})

add_subdirectory("sDNA/sdna_vs2008", "output")


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


add_custom_target(${PROJECT_NAME} ALL)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${Scripts}" "output/$<CONFIG>"
)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${ScriptsBin}" "output/$<CONFIG>/bin"
)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "${InstallerBits}" "output/$<CONFIG>"
)

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory_if_different  "arcscripts/rportable" "output/$<CONFIG>/rportable"
)
