@echo off

set CWD=%cd%

if [%1%]==[] ( 
    set VER_NUM=%RELEASE%) else ( set VER_NUM=%1)

if [%2%]==[] ( 
    set PLATFORM_=%PLATFORM%) else ( set PLATFORM_=%2)

if [%3%]==[] ( 
    set CONFIG_=%CONFIGURATION%) else ( set CONFIG_=%3)

if [%4%]==[] ( 
    set GEOS_=%GEOS_VERSION%) else ( set GEOS_=%4)

if [%5%]==[] ( 
    set BOOST_=%BOOST_VERSION%) else ( set BOOST_=%5)

set RELEASE_FILE_NAME=sDNA_lite_v%VER_NUM%_%PLATFORM_%_%CONFIG_%_osgeo4w_geos_v%GEOS_%_Boost_v%BOOST_%_RTTI_on

if [%CONFIG_%]==[Release] ( 
    set BUILD_CONFIG=release) else ( set BUILD_CONFIG=%CONFIG_%)

set DIR_TO_ZIP=%~dp0\output\%BUILD_CONFIG%

cd %DIR_TO_ZIP%

tar -a -cf %CWD%\%RELEASE_FILE_NAME%.zip *
tar -j -cf %CWD%\%RELEASE_FILE_NAME%.tar.bz2 *

cd %CWD%