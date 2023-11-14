@echo off

set BUILD_DIR=%TMP%\sDNA_build_geos\geos
REM Forward errors to nul in case BUILD_DIR already exists
mkdir %BUILD_DIR% > nul 2> nul

@echo on
curl -L -o %BUILD_DIR%\geos_archive.tar.bz2 https://download.osgeo.org/osgeo4w/v2/x86_64/release/geos/geos-3.12.0-1.tar.bz2
@echo off

set CWD=%cd%
cd %BUILD_DIR%
tar -xf geos_archive.tar.bz2
move bin\geos_c.dll %~dp0\output\release\x64
cd %CWD%
