cmake_minimum_required(VERSION 3.20)

# set CMAKE_TOOLCHAIN_FILE in CMakePresets.json as recommended
# https://learn.microsoft.com/en-gb/vcpkg/users/buildsystems/cmake-integration#cmake_toolchain_file
# set(CMAKE_TOOLCHAIN_FILE
#   ../vcpkg/scripts/buildsystems/vcpkg.cmake
#   )

# "The version of the operating system for which CMake is to build."
# https://cmake.org/cmake/help/latest/variable/CMAKE_SYSTEM_VERSION.html
set(CMAKE_SYSTEM_VERSION 10.0 CACHE STRING "" FORCE)


# set CMAKE_TOOLCHAIN_FILE in CMakePresets.json as recommended
# https://learn.microsoft.com/en-gb/vcpkg/users/buildsystems/cmake-integration#cmake_toolchain_file
# Alternatively add this line:
set(CMAKE_TOOLCHAIN_FILE
 "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
 )

set(PROJECT_NAME sdna_vs2008)

# "This will become the name of the resulting Visual Studio solution. "
# https://cmake.org/cmake/help/book/mastering-cmake/chapter/Converting%20Existing%20Systems%20To%20CMake.html#converting-windows-based-workspaces
project(${PROJECT_NAME} CXX)

# In CMake, the target Platform can be set for all Visual Studio Generators 
# as far back as VS 2008 by setting
# https://cmake.org/cmake/help/latest/generator/Visual%20Studio%2017%202022.html

# CMAKE_VS_PLATFORM_NAME can be set via CMAKE_GENERATOR_PLATFORM
# https://cmake.org/cmake/help/latest/variable/CMAKE_GENERATOR_PLATFORM.html#variable:CMAKE_GENERATOR_PLATFORM

# https://cmake.org/cmake/help/latest/variable/CMAKE_VS_PLATFORM_NAME.html#cmake-vs-platform-name
################################################################################
# Set target arch type if empty. Visual studio solution generator provides it.
################################################################################
if(NOT CMAKE_VS_PLATFORM_NAME)
    set(CMAKE_VS_PLATFORM_NAME "x64")
endif()

set(Supported_platforms
  "Any CPU"  
  "Mixed Platforms"                                     
  "Win32"                              
  "x64"
  )

if ("${CMAKE_VS_PLATFORM_NAME}" IN_LIST Supported_platforms)  
   message("${CMAKE_VS_PLATFORM_NAME} architecture in use")
else()
    message(FATAL_ERROR "${CMAKE_VS_PLATFORM_NAME} arch is not supported!")
endif()

# "For multi-configuration generators like Visual Studio, Xcode, 
# and Ninja Multi-Config, the configuration is chosen by the user 
# at build time and CMAKE_BUILD_TYPE is ignored. "
# https://cmake.org/cmake/help/git-master/manual/cmake-buildsystem.7.html#build-configurations
# https://cmake.org/cmake/help/latest/command/set.html#set-cache-entry
#
################################################################################
# Global configuration types
################################################################################
#
# https://cmake.org/cmake/help/book/mastering-cmake/chapter/Getting%20Started.html#build-configurations
# https://cmake.org/cmake/help/latest/variable/CMAKE_CONFIGURATION_TYPES.html#variable:CMAKE_CONFIGURATION_TYPES
set(CMAKE_CONFIGURATION_TYPES
    "Debug"
    "Debug_speedup"
    "Debug64"
    "fast_debug"
    "parallel_debug"
    "package"
    "benchmark_probroutes"
    "prob_route_release"
    "Release"
    "vtune"
    CACHE STRING "" FORCE
)

################################################################################
# Global compiler options
################################################################################
if(MSVC)
    # remove default flags provided with CMake for MSVC
    set(CMAKE_CXX_FLAGS "")
    set(CMAKE_CXX_FLAGS_BENCHMARK_PROBROUTES "")
    set(CMAKE_CXX_FLAGS_DEBUG "")
    set(CMAKE_CXX_FLAGS_DEBUG_SPEEDUP "")
    set(CMAKE_CXX_FLAGS_FAST_DEBUG "")
    set(CMAKE_CXX_FLAGS_PARALLEL_DEBUG "")
    set(CMAKE_CXX_FLAGS_RELEASE "")
    set(CMAKE_CXX_FLAGS_VTUNE "")
    set(CMAKE_CXX_FLAGS_DEBUG64 "")
    set(CMAKE_CXX_FLAGS_PACKAGE "")
    set(CMAKE_CXX_FLAGS_PROB_ROUTE_RELEASE "")
endif()

################################################################################
# Global linker options
################################################################################
if(MSVC)
    # remove default flags provided with CMake for MSVC
    set(CMAKE_EXE_LINKER_FLAGS "")
    set(CMAKE_MODULE_LINKER_FLAGS "")
    set(CMAKE_SHARED_LINKER_FLAGS "")
    set(CMAKE_STATIC_LINKER_FLAGS "")
    set(CMAKE_EXE_LINKER_FLAGS_BENCHMARK_PROBROUTES "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_BENCHMARK_PROBROUTES "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_BENCHMARK_PROBROUTES "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_BENCHMARK_PROBROUTES "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_DEBUG "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_DEBUG "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_DEBUG_SPEEDUP "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_DEBUG_SPEEDUP "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG_SPEEDUP "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_DEBUG_SPEEDUP "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_FAST_DEBUG "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_FAST_DEBUG "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_FAST_DEBUG "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_FAST_DEBUG "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_PARALLEL_DEBUG "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_PARALLEL_DEBUG "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_PARALLEL_DEBUG "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_PARALLEL_DEBUG "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_RELEASE "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_RELEASE "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_VTUNE "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_VTUNE "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_VTUNE "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_VTUNE "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_DEBUG64 "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_DEBUG64 "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG64 "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_DEBUG64 "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_PACKAGE "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_PACKAGE "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_PACKAGE "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_PACKAGE "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_PROB_ROUTE_RELEASE "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_PROB_ROUTE_RELEASE "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_PROB_ROUTE_RELEASE "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_PROB_ROUTE_RELEASE "${CMAKE_STATIC_LINKER_FLAGS}")
endif()


################################################################################
# Common utils
################################################################################
include(CMake/Utils.cmake)


################################################################################
# Use solution folders feature
################################################################################
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

################################################################################
# Sub-projects
################################################################################

set(boost_packages
  "algorithm"
  "bimap"
  "chrono"
  "date-time"
  "foreach"
  "geometry"
  "iterator"
  "lexical-cast"
  "math"
  "mpl"
  "numeric-conversion"
  "pool"
  "random"
  "smart-ptr"
  "static-assert"
  "system"
  "thread"
  "type-traits"
  "utility"
  "variant"
)

# foreach(boost_package IN LISTS boost_packages)
#   find_package(${boost_package} REQUIRED)
# endforeach()

# # https://cmake.org/cmake/help/latest/module/FindBoost.html#boost-cmake
# find_package(Boost 1.83 EXACT
#   REQUIRED COMPONENTS ${boost_packages}
# )

find_package(Boost REQUIRED)

include_directories(${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})


################################################################################
# Source groups
################################################################################
set(Headers
    "calculation.h"
    "calculationbase.h"
    "config_string_parser.h"
    "dataacquisitionstrategy.h"
    "edge.h"
    "geos_sdna_wrapper.h"
    "linkdatasource.h"
    "metricevaluator.h"
    "net.h"
    "point.h"
    "prepareoperations.h"
    "random.h"
    "sdna.h"
    "sdna_arrays.h"
    "sdna_geometry_collections.h"
    "sdna_output_utils.h"
    "sdna_spatial_accumulators.h"
    "sDNACalculationFactory.h"
    "stdafx.h"
    "tables.h"
    "targetver.h"
    "unique_id.h"
    "version_template.h"
    "version_generated.h.creator.py"
)
source_group("Headers" FILES ${Headers})

set(MuParser
    "../muparser/drop/src/muParser.cpp"
    "../muparser/drop/src/muParserBase.cpp"
    "../muparser/drop/src/muParserBytecode.cpp"
    "../muparser/drop/src/muParserCallback.cpp"
    "../muparser/drop/src/muParserError.cpp"
    "../muparser/drop/src/muParserTokenReader.cpp"
)
source_group("MuParser" FILES ${MuParser})

set(Sources
    "calc_output_code.cpp"
    "calculation.cpp"
    "dijkstra.cpp"
    "dllmain.cpp"
    "edge.cpp"
    "geos_sdna_wrapper.cpp"
    "interface_funcs.cpp"
    "metricevaluator.cpp"
    "net.cpp"
    "prepareoperations.cpp"
    "random.cpp"
    "sdna_geometry_collections.cpp"
    "sDNACalculationFactory.cpp"
    "stdafx.cpp"
    "unit_tests.cpp"
)
source_group("Sources" FILES ${Sources})


set(ALL_FILES
    ${Headers}
    ${Sources}
    ${MuParser}
)

################################################################################
# Target
################################################################################

# " Next, add all of your source files into CMake variables. 
# For large projects that have multiple directories, 
# create a CMakeLists file in each directory 
# as described in the section on source directory structures 
# at the beginning of this chapter. "
#
# " If you add header files to a target, they will show up in 
# the workspace and then you will be able to browse them as usual. "

# "Visual Studio also supports the notion of groups of files. 
#  By default, CMake creates groups for source files and header files. 
#  Using the source_group command, you can create your own groups 
#  and assign files to them. "

# "You will then add your libraries and executables using add_library and add_executable."
# https://cmake.org/cmake/help/latest/command/add_library.html#command:add_library
#  add_library(<name> [<type>] [EXCLUDE_FROM_ALL] <sources>...)
# "CMake expects a SHARED library to always have an associated import library on Windows."
add_library(${PROJECT_NAME} SHARED ${ALL_FILES})


target_link_libraries(${PROJECT_NAME} PUBLIC ${Boost_LIBRARIES})

target_precompile_headers(${PROJECT_NAME} PRIVATE "stdafx.h")

use_props(${PROJECT_NAME} "${CMAKE_CONFIGURATION_TYPES}" "${DEFAULT_CXX_PROPS}")
set(ROOT_NAMESPACE sdna_vs2008)

set_target_properties(${PROJECT_NAME} PROPERTIES
    VS_GLOBAL_KEYWORD "Win32Proj"
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    INTERPROCEDURAL_OPTIMIZATION_BENCHMARK_PROBROUTES "TRUE"
    INTERPROCEDURAL_OPTIMIZATION_FAST_DEBUG           "TRUE"
    INTERPROCEDURAL_OPTIMIZATION_RELEASE              "TRUE"
)

################################################################################
# MSVC runtime library
################################################################################
get_property(MSVC_RUNTIME_LIBRARY_DEFAULT TARGET ${PROJECT_NAME} PROPERTY MSVC_RUNTIME_LIBRARY)
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Any CPU")
    string(CONCAT "MSVC_RUNTIME_LIBRARY_STR"
        $<$<CONFIG:benchmark_probroutes>:
            MultiThreaded
        >
        $<$<CONFIG:Debug_speedup>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:fast_debug>:
            MultiThreaded
        >
        $<$<CONFIG:parallel_debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Release>:
            MultiThreaded
        >
        $<$<CONFIG:vtune>:
            MultiThreadedDebug
        >
        $<$<NOT:$<OR:$<CONFIG:benchmark_probroutes>,$<CONFIG:Debug_speedup>,$<CONFIG:Debug>,$<CONFIG:fast_debug>,$<CONFIG:parallel_debug>,$<CONFIG:Release>,$<CONFIG:vtune>>>:${MSVC_RUNTIME_LIBRARY_DEFAULT}>
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Mixed Platforms")
    string(CONCAT "MSVC_RUNTIME_LIBRARY_STR"
        $<$<CONFIG:benchmark_probroutes>:
            MultiThreaded
        >
        $<$<CONFIG:Debug_speedup>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:fast_debug>:
            MultiThreaded
        >
        $<$<CONFIG:parallel_debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Release>:
            MultiThreaded
        >
        $<$<CONFIG:vtune>:
            MultiThreadedDebug
        >
        $<$<NOT:$<OR:$<CONFIG:benchmark_probroutes>,$<CONFIG:Debug_speedup>,$<CONFIG:Debug>,$<CONFIG:fast_debug>,$<CONFIG:parallel_debug>,$<CONFIG:Release>,$<CONFIG:vtune>>>:${MSVC_RUNTIME_LIBRARY_DEFAULT}>
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    string(CONCAT "MSVC_RUNTIME_LIBRARY_STR"
        $<$<CONFIG:benchmark_probroutes>:
            MultiThreaded
        >
        $<$<CONFIG:Debug_speedup>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:fast_debug>:
            MultiThreaded
        >
        $<$<CONFIG:parallel_debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Release>:
            MultiThreaded
        >
        $<$<CONFIG:vtune>:
            MultiThreadedDebug
        >
        $<$<NOT:$<OR:$<CONFIG:benchmark_probroutes>,$<CONFIG:Debug_speedup>,$<CONFIG:Debug>,$<CONFIG:fast_debug>,$<CONFIG:parallel_debug>,$<CONFIG:Release>,$<CONFIG:vtune>>>:${MSVC_RUNTIME_LIBRARY_DEFAULT}>
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    string(CONCAT "MSVC_RUNTIME_LIBRARY_STR"
        $<$<CONFIG:benchmark_probroutes>:
            MultiThreaded
        >
        $<$<CONFIG:Debug_speedup>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:fast_debug>:
            MultiThreaded
        >
        $<$<CONFIG:parallel_debug>:
            MultiThreadedDebug
        >
        $<$<CONFIG:Release>:
            MultiThreaded
        >
        $<$<CONFIG:vtune>:
            MultiThreadedDebug
        >
        $<$<NOT:$<OR:$<CONFIG:benchmark_probroutes>,$<CONFIG:Debug_speedup>,$<CONFIG:Debug>,$<CONFIG:fast_debug>,$<CONFIG:parallel_debug>,$<CONFIG:Release>,$<CONFIG:vtune>>>:${MSVC_RUNTIME_LIBRARY_DEFAULT}>
    )
endif()
set_target_properties(${PROJECT_NAME} PROPERTIES MSVC_RUNTIME_LIBRARY ${MSVC_RUNTIME_LIBRARY_STR})

################################################################################
# Include directories
################################################################################
target_include_directories(${PROJECT_NAME} PUBLIC
    "../muparser/drop/include"
)

################################################################################
# Compile definitions
################################################################################
target_compile_definitions(${PROJECT_NAME} PRIVATE
"$<$<CONFIG:benchmark_probroutes>:"
    "NDEBUG;"
    "BENCHMARK;"
    "PROB_ROUTE_CODE"
">"
"$<$<CONFIG:Debug_speedup>:"
    "_DEBUG"
">"
"$<$<CONFIG:Debug>:"
    "_DEBUG;"
    "_SDNADEBUG"
">"
"$<$<CONFIG:fast_debug>:"
    "NDEBUG"
">"
"$<$<CONFIG:parallel_debug>:"
    "_DEBUG;"
    "_SDNADEBUG"
">"
"$<$<CONFIG:Release>:"
    "NDEBUG"
">"
"$<$<CONFIG:vtune>:"
    "_DEBUG"
">"
"WIN32;"
"_WINDOWS;"
"_USRDLL;"
"SDNA_VS2008_EXPORTS;"
"UNICODE;"
"_UNICODE"
)

################################################################################
# Compile and link options
################################################################################
if(MSVC)
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Any CPU")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:Debug_speedup>:
                /O2;
                /Zi;
                /Ot;
                /openmp
            >
            $<$<CONFIG:Debug>:
                /Od;
                /RTC1;
                /Zi;
                
            >
            $<$<CONFIG:fast_debug>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:parallel_debug>:
                /Od;
                /RTC1;
                /Zi;
                
            >
            $<$<CONFIG:Release>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:vtune>:
                /Od;
                /RTC1;
                /ZI;
                
            >
            /Gm-;
            /W3;
            /fp:precise;
            /Zm140;
            ${DEFAULT_CXX_EXCEPTION_HANDLING}
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Mixed Platforms")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:Debug_speedup>:
                /O2;
                /Zi;
                /Ot;
                /openmp
            >
            $<$<CONFIG:Debug>:
                /Od;
                /RTC1;
                /Zi;
                
            >
            $<$<CONFIG:fast_debug>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:parallel_debug>:
                /Od;
                /RTC1;
                /Zi;
                
            >
            $<$<CONFIG:Release>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:vtune>:
                /Od;
                /RTC1;
                /ZI;
                
            >
            /Gm-;
            /W3;
            /fp:precise;
            /Zm140;
            ${DEFAULT_CXX_EXCEPTION_HANDLING}
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:Debug_speedup>:
                /O2;
                /Zi;
                /Ot;
                /openmp
            >
            $<$<CONFIG:Debug>:
                /Od;
                /RTC1;
                /Zi;
                
            >
            $<$<CONFIG:fast_debug>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:parallel_debug>:
                /Od;
                /RTC1;
                /Zi;
                /openmp
            >
            $<$<CONFIG:Release>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Zi;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:vtune>:
                /Od;
                /RTC1;
                /ZI;
                
            >
            /Gm-;
            /W3;
            /fp:precise;
            /Zm140;
            ${DEFAULT_CXX_EXCEPTION_HANDLING}
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:Debug_speedup>:
                /O2;
                /Ot;
                /openmp
            >
            $<$<CONFIG:Debug>:
                /Od;
                /RTC1;
                
            >
            $<$<CONFIG:fast_debug>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Ot;
                /GR-;
                /GS-;
                /openmp
            >
            $<$<CONFIG:parallel_debug>:
                /Od;
                /RTC1;
                
            >
            $<$<CONFIG:Release>:
                /O2;
                /Ob2;
                /Oi;
                /Gy-;
                /Ot;
                /GR;
                /GS-;
                /openmp
            >
            $<$<CONFIG:vtune>:
                /Od;
                /RTC1;
                
            >
            /Gm-;
            /W3;
            /Zi;
            /fp:precise;
            /Zm140;
            ${DEFAULT_CXX_EXCEPTION_HANDLING}
        )
    endif()

    string(CONCAT FILE_CL_OPTIONS
        "/Zm140"
    )
    source_file_compile_options(stdafx.cpp ${FILE_CL_OPTIONS})
    
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Any CPU")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /MACHINE:X86;
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:Debug_speedup>:
                /MACHINE:X86;
                /INCREMENTAL
            >
            $<$<CONFIG:Debug>:
                /MACHINE:X86;
                /INCREMENTAL
            >
            $<$<CONFIG:fast_debug>:
                /MACHINE:X86;
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:parallel_debug>:
                /MACHINE:X64;
                /INCREMENTAL
            >
            $<$<CONFIG:Release>:
                /MACHINE:X86;
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:vtune>:
                /MACHINE:X86;
                /INCREMENTAL
            >
            /DEBUG;
            /SUBSYSTEM:WINDOWS
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Mixed Platforms")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /MACHINE:X86;
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:Debug_speedup>:
                /MACHINE:X86;
                /INCREMENTAL
            >
            $<$<CONFIG:Debug>:
                /MACHINE:X86;
                /INCREMENTAL
            >
            $<$<CONFIG:fast_debug>:
                /MACHINE:X86;
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:parallel_debug>:
                /MACHINE:X64;
                /INCREMENTAL
            >
            $<$<CONFIG:Release>:
                /MACHINE:X86;
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:vtune>:
                /MACHINE:X86;
                /INCREMENTAL
            >
            /DEBUG;
            /SUBSYSTEM:WINDOWS
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:Debug_speedup>:
                /INCREMENTAL
            >
            $<$<CONFIG:Debug>:
                /INCREMENTAL
            >
            $<$<CONFIG:fast_debug>:
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:parallel_debug>:
                /INCREMENTAL
            >
            $<$<CONFIG:Release>:
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:vtune>:
                /INCREMENTAL
            >
            /DEBUG;
            /MACHINE:X86;
            /SUBSYSTEM:WINDOWS
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:benchmark_probroutes>:
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:Debug_speedup>:
                /INCREMENTAL
            >
            $<$<CONFIG:Debug>:
                /INCREMENTAL
            >
            $<$<CONFIG:fast_debug>:
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:parallel_debug>:
                /INCREMENTAL
            >
            $<$<CONFIG:Release>:
                /OPT:REF;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            $<$<CONFIG:vtune>:
                /INCREMENTAL
            >
            /DEBUG;
            /MACHINE:X64;
            /SUBSYSTEM:WINDOWS
        )
    endif()
endif()

################################################################################
# Pre build events
################################################################################
#
# "If you have any custom build steps in your workspace, 
# these can be added to your CMakeLists files using the 
# add_custom_command command. Custom targets (Utility Targets) 
# in Visual Studio can be added with the add_custom_target command. "
# https://cmake.org/cmake/help/book/mastering-cmake/chapter/Converting%20Existing%20Systems%20To%20CMake.html#converting-windows-based-workspaces
#
# "PRE_BUILD
#     This option has unique behavior for the Visual Studio Generators. 
# When using one of the Visual Studio generators, the command will run 
# before any other rules are executed within the target. With all other 
# generators, this option behaves the same as PRE_LINK instead. 
# Because of this, it is recommended to avoid using PRE_BUILD except when 
# it is known that a Visual Studio generator is being used.
#
# PRE_LINK
#     Run after sources have been compiled but before linking the binary 
# or running the librarian or archiver tool of a static library. This is 
# not defined for targets created by the add_custom_target() command.
# "
# https://cmake.org/cmake/help/latest/command/add_custom_command.html#build-events
add_custom_command(
    TARGET ${PROJECT_NAME} PRE_BUILD
    COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}"/version_generated.h.creator.py"
    # COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}"/sDNA/sdna_vs2008/version_generated.h.creator.py"
)


