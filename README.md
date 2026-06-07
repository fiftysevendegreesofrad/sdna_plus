# sDNA+: Spatial Design Network Analysis plus

This is the experimental [Cross Platform](https://github.com/fiftysevendegreesofrad/sdna_plus/tree/Cross_platform) branch of sDNA+, now available for Linux as well as Windows.

## Quick start

If not already available, install [`pipx`](https://github.com/pypa/pipx) to automatically 
install Python applications into virtual environments (avoiding Python dependency conflicts):
```
pip install pipx
```

Use pipx to install an sDNA Wheel from PyPi:
```
pipx install sdna_plus
```

Example command line use:
```
sdnaintegral -i input_network.shp -o output_network.shp`
```

### To use sDNA Learn or sDNA Predict
The `[learn]` or `[predict]` optional dependencies (including Numpy) are also required (Numpy 2 needs ~35MB).  
As is an installation of [`R`](https://www.r-project.org/) with optparse and Car.

#### On Linux 

Install R and the two deps separately, e.g. on Ubuntu with:
```
sudo apt-get update
sudo apt-get install -y r-cran-optparse r-cran-sjstats
pipx install sdna_plus[learn]
```

#### Using R Portable 3.2.3 (Windows only). 
This is the same [R-Portable](https://github.com/JamesParrott/rportable) as bundled 
with sDNA previously.  Requires ~100MB.
```
pipx install sdna_plus[learn,R]
```




## Notes
On Linux there are five unsolved regressions (compared to the Windows build), which may or may not be important.
See issues #61, #65, #83, #84, and #83.

The Linux Wheel, including `geos_c.so` as well as `sdna_vs2008.so` is built in a Docker image based on the 
oldest (now unsupported) ManyLinux image.  See `Dockerfile.build`.  It is compiled with GCC 4.8 ish, so 
different run time behaviour is possible between it and both the GCC and zig c++ Linux builds.  A 
build hook (`./hatch_build.py`) triggers a near normal CMake build of sDNA, and Hatchling 
repackages the standard sDNA output directory for PyPi (instead of just zipping it 
or running AdvancedInstaller on Windows).

## History

This is the open source fork of the formerly proprietary sDNA+ software - all the sDNA features plus hybrid metrics. 

sDNA+ was created by Crispin Cooper on behalf of [Cardiff University](https://www.cardiff.ac.uk).  Alain Chiaradia was responsible for the initial idea, and Chris Webster for the initial funding and project mentoring. We are grateful to various parties for financial contributions towards development: in no particular order, Hong Kong University, Tongji University, the UK Economic and Social Research Council, BRE, Wedderburn Transport Planning. Also research contributions in kind from Arup Ltd, WSP Global Engineering, BuroHappold and Sustrans. Also to James Parrott both for developing the [sDNA for Grasshopper](https://github.com/fiftysevendegreesofrad/sDNA_GH) plugin, and for assistance in updating the sDNA build process during 2023. And Jeffrey Morgan for updating sDNA to Python 3.

If you are interested in sponsoring changes to sDNA, please get in touch with Crispin cooperch@cardiff.ac.uk.

Copyright rests with Cardiff University and the code is released under GPL Affero version 3.

## For Users

### Installation

Use the software via any of the following means:

* QGIS 2.14 onwards
  * as well as installing sDNA, you will need to install the sDNA QGIS plugin from the QGIS plugins dialog.
* ArcGIS 10.2 onwards, and ArcGIS Pro
  * as well as installing sDNA, you will need to add the toolbox found in the sDNA install folder to the Arc toolbox. 
* Autocad
  * We discountinued the old Autocad interface as it doesn't process attached data. If using Autocad, we recommend export/import of shapefiles using Autocad Map3d, then use sDNA from the free QGIS
* Add the `bin` folder to your path and use sDNA command line scripts
  * To see examples of command line calls, run sDNA from QGIS, the plugin will tell you what command line it uses for each task
* Use the Python interface `sdnapy.py`; look at `runcalculation.py` for the reference example of how to do this

### Documentation

Hosted on [readthedocs](https://sdna-plus.readthedocs.io/en/latest/).

### Support

Please see the original project [support page](https://sdna.cardiff.ac.uk/sdna/support/).

If filing a bug, please file to [the database here on github](https://github.com/fiftysevendegreesofrad/sdna_plus/issues). 

## For Developers
See BUILD.md for notes regarding the impact of switching to CMake from sdna_vs2008.vcxproj

### Experimental Linux build
Requires the `Cross_platform` branch.  The GCC builds are prioritised, but the 'Clang' builds (using `zig c++`) have been invaluable.
There are  a handful of open regressions (compared to the Windows build), which may or may not be important.
#### Installation
* Build from source (see `./BUILD.md`) or if on Ubuntu, download and unzip an "output" installation directory from a Github Action that built it ([e.g.](https://github.com/fiftysevendegreesofrad/sdna_plus/actions/runs/9584489142)).  If the artifacts have expired, a public fork can
be made, on which Github Actions can be run for free.  Using this, the "CMake, GCC & Ubuntu" one will rebuild it for
you automatically in about 5 minutes.  The copy of `libgeos_c.so` may require a specific version of glibc.  If this is not available, it will have to be recompiled (see `./BUILD.md` or `.github/workflows/build_geos.yml`).
* Create a venv and activate it (to avoid installing packages into the operating system's Python, and to isolate Numpy).
* Install PyShp: `pip install -r requirements.txt`
* The entry points in './bin' should be able to be used as normal.
* The Python API may first require: `SDNADLL=/path/to/output/Release/x64/sdna_vs2008.so`  
* If sDNA Learn or Predict is required:
  - Numpy must be installed: `pip install -r requirements-learn-predict.txt`
  - R (and the "optparser" and "can" packages) must be installed separately, e.g. on Ubuntu: 
```
sudo apt-get update
sudo apt-get install -y r-cran-optparse r-cran-sjstats
```
### Building the software

#### Local build requirements:

* Microsoft Visual Studio (tested on 2022) with C++ extensions
* Python
* Advanced Installer.  Add the location of `AdvancedInstaller.com` either to your path (`%PATH%`) or to line 8 of `build_installer.proj`.
* Vcpkg (tested with vcpkg.exe `version 2024-04-23-d6945642ee5c3076addd1a42c331bbf4cfc97457`).  E.g. in the chosen parent dir:
   - `git clone --depth=1 https://github.com/microsoft/vcpkg/`
   - `cd vcpkg`
   - `setx VCPKG_ROOT c:\path_to_vcpkg_repo\vcpkg`
   - `.\bootstrap-vcpkg.bat`
* 5-6 GB free disk space (to be safe).

Fire up the Visual Studio Developer Command Prompt. 
 - Before the first use of vcpkg, in the vcpkg repo root call [`.\vcpkg.exe integrate install`](https://learn.microsoft.com/en-gb/vcpkg/users/buildsystems/msbuild-integration)
 - Then in the sDNA repo's root call `build_release.bat` which should do what it says on the tin.

#### CI build and test requirements:
* Run the Github Action `.github\workflows\compile_and_test.yml`

#### CMake build requirements:
* CMake (tested on 3.27.7.  At least 3.16 is required for precompiled headers),
* as for "Local build requirements" above (without Advanced Installer and without integrating vcpkg).
* To build in cmd (or a shell with a character limit too low for CMake and the deeply nested R-portable tree) it may be
necessary to open an admin Powershell terminal and run: 
```
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" 
-Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```
CMake ideally wants build trees to be separate from source trees.  But in order 
for `sDNA\sdna_vs2008\version_generated.h.creator.py` to be able to extract a commit hash, 
the build tree must at the very least live within a copy of the sDNA Git repo.  So for now 
we'll pretend the source tree is `.\sDNA\` and put the 'build tree' in `.\build_cmake`.

CMake's Visual Studio Generator is a multi-config generator.  This would be handy for
creating a Release build in parallel with a Debug build.  Unfortunately it is not a 
multi-platform generator (sDNA's installer contains Release Win32 and Release x64 DLLs).
CMakeLists.txt needs to be invoked and built from twice therefore, to produce a Windows installer.

Running (in a normal cmd.exe, not the VS Developer Command Prompt):
 - `.\create_installer_with_CMake.bat`
should create `sDNA_setup_win_vX.msi`.

### Dependencies

#### Boost
It is not immediately visible, but Boost 1.83 is used currently. Vcpkg manifest mode uses hashes of git commits of its own repo to define baselines from which dependencies are drawn.  These are in `sDNA\sdna_vs2008\vcpkg-configuration.json`.  For example `61f610845fb206298a69f708104a51d651872877` refers to https://github.com/microsoft/vcpkg/commit/61f610845fb206298a69f708104a51d651872877 of Nov 11th 2023, on which date the latest version of Boost in vcpkg was 1.83
https://learn.microsoft.com/en-gb/vcpkg/consume/boost-versions

It is possible to use an override mechanism to pin deps instead, but this would make `sDNA\sdna_vs2008\vcpkg.json` much longer.  https://learn.microsoft.com/en-gb/vcpkg/consume/lock-package-versions?tabs=inspect-powershell#5---force-a-specific-version

#### Geos
Geos v3.3.5 is dynamically linked at run-time.  A custom build step copies in the `geos_c.dll`s (from `sDNA\geos\x64\src`
and `sDNA\geos\x86\src`), originally compiled for OSGEO4W available hereabouts: https://download.osgeo.org/osgeo4w/v2/x86_64/release/geos/ .  On Linux `geos_c.so` is first compiled in the build environment, see e.g. `.github\workflows\build_geos.yml` 
or in the oldest manylinux image for greatest compatibility: `Dockerfile.build`.

#### Muparser
A static copy of [`Rev 2.2.3: 22.12.2012`](https://launchpad.net/ubuntu/+source/muparser/2.2.3-6).  Changes:
 * `#define MUP_BASETYPE float` in sDNA\muparser\drop\include\muParserDef.h
At build time on Windows, using MSVC and MSBuild (no CMake), the source code is dynamically changed.
A custom prebuild step (`sDNA\sdna_vs2008\preppend_muparser_cpps_with_include_stdafx.h.py`) makes each Muparser file
compatible with Visual Studio's particular (not force included) pre-compiled header rules.

#### Anyiterator
```
// Revision History
// ================
//
// 12 Jul 2010 
```
#### R-portable
Version 3.2.3.  Available here: https://sourceforge.net/projects/rportable/files/

### Packaging
The Windows installer contains x64 and Win32 binaries (for both `sdna_vs2008.dll` and `geos_c.dll`)

### Project Structure

Some key folders:

* `sDNA` - C++ projects
  * `sdna_vs2008` - the core sDNA dll
  	* `tests` - tests of the above
  * `geos`, `muparser` - dependencies of `sdna_vs2008`
* `arcscripts` - originally just for ArcGIS, now also comprises the QGIS, Python and command line interface
  * `bin` - command line tools
  * `sdnapy.py` - python interface
  * `sDNAUISpec.py` - defines user interface for both ArcGIS and QGIS
    * ArcGIS interprets this via `sDNA.pyt`
    * QGIS code to interpret this is found in the [QGIS sDNA Plugin](https://plugins.qgis.org/plugins/sdna/)
* `installerbits` - extras needed to create install package
* `docs` - documentation

### Tests

The test code needs updating (plan to do this with the port to Linux).

#### Continuous Integration Tests.

Currently, the CI tests are a subset of sDNA's regression tests, which diff the test output against that produced by a previous build (eight of the expected output files can be recreated using `sDNA\sdna_vs2008\tests\approve_debug_output.bat`, but `correctout_learn.txt` and `correctout_table.txt` require other means).

The CI test runner parses every `.bat` file in `sDNA\sdna_vs2008\tests` except the following which are filtered out:
`colourdiff.bat`, `mydiff.bat`, `awkward_test.bat`, `arc_script_test.bat`,`run_tests_windows.bat`, `sdnavars64.bat`,`quick_test.bat` ( as it reruns `debug_test.py` which is already tested in `pause_debug_test.bat`) and `run_benchmark.bat` (to avoid issue 11, an unexplained "Access violation on Python 3").

To run the CI tests locally, something like the following commands are required:

```
cd your_venvs_directory
python -m venv sdna_testing_venv
.\sdna_testing_venv\Scripts\activate
pip install numpy pytest
cd path_to_sdna_plus_repo\sdna_plus\sDNA\sdna_vs2008\tests\pytest
set DONT_TEST_N_LINK_SUBSYSTEMS_ORDER=1 & set ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT=1 & pytest -rA
```

The CI test runner is designed to use Pytest, but can also run its tests only requiring pytest as an import (if run as a script).  It is influenced by the following environment variables:
 - `sdna_debug` - By default it is assumed release builds are tested, so this is Falsey - i.e. an empty string (do not use 0 or "False" as in Python `bool("0") is True` and `bool("False") is True`).  If so, then the output lines resulting from the parts of sDNA's C++ source code, that are only compiled if the pre_processor directive `_SDNADEBUG` is set, are omitted from the "expected" output.  Set this to something Truthy (any non-empty string other than `False`) if testing a debug build.
 - `sdna_dll` - the path to the `sdna_vs2008.dll` to test.  By default the test runner tries to run a fair test, by using the Python files associated with an sDNA installation, or those in a repo containing a `sdna_vs2008.dll` resulting from running the compilation process.  It is also possible to set `sdna_bin_dir` to any directory containing the required sDNA `.py` files.
 - `DONT_TEST_N_LINK_SUBSYSTEMS_ORDER` - must be set to something Truthy, to work around issue 20.
 - `ALLOW_NEGATIVE_FORMULA_ERROR_ON_ANY_LINK_PRESENT` - must be set to something Truthy, to work around issue 21.

Various other quality of life adjustments are made, such as ignoring blank lines, and Progress bar percentage lines.

#### Old testing routine.

Currently the steps outlined below may not work, but what *does* work is setting appriate paths for `python2exe`, `python3exe`, and `sdnadll` (which should be 32 or 64 bit depending on the Python executable) then calling `pause_debug_test.bat`.

For testing the core network processing and numerical routines, fire up the `sdna_vs2008.sln` solution in `sDNA\sDNA_vs2008`. 
You will need the correct debug settings; unfortunately Visual Studio stores these with user information. Copy `sdna\sdna_vs2008\sdna_vs2008.vcproj.octopi.Crispin.user.sample` on top of your own `sdna_vs2008.vcproj.yourmachine.yourusername.user` file.
Set build configuration to `Debug Win32`, and run. This calls scripts in `sDNA\sDNA_vs2008\tests` and diffs the output with correct outputs (the core of which are originally hand computed) in that directory. Any call to `diff` that shows differences is a test fail.

For `test_parallel_results.py` to work, you also need to build the `parallel_debug Win32` configuration. When `Debug Win32` is run as described above, serial and parallel results are compared to check they are identical.

Interfaces are not automatically tested, though `arcscripts\sdna_environment.py` can be tested by `environment_test.py`.

### Future

The long term roadmap includes moving to reproducible builds (which will be nice when developers have to onboard or change machines), and porting to Linux. We think the path towards this is (1) replace MSBuild with cmake (there is a converter); (2) replace msvc with gcc; (3) the community profits!

## License

The bulk of sDNA+ is licensed under GNU Affero v3, with various other Free licenses for various modules. For full details see [licensing](LICENSE.md).
   
