# sDNA+: Spatial Design Network Analysis plus

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

If filing a bug, please file to the database here on github. 

## For Developers

### Building the software

#### Local build requirements:

* Microsoft Visual Studio (tested on 2022) with C++ extensions
* Python 2.7
* Advanced Installer
* Vcpkg built from commit `d6945642......` (`2024-04-23-`).  E.g. in the dir to install it in:
   - `git clone --depth=1 https://github.com/microsoft/vcpkg/`
   - `cd vcpkg`
   - `.\bootstrap-vckg.bat`
* 5-6 GB free disk space (to be safe).

Fire up the Visual Studio Developer Command Prompt. 
 - Before the first use of vcpkg, in the vcpkg repo root call [`.\vcpkg.exe integrate install`](https://learn.microsoft.com/en-gb/vcpkg/users/buildsystems/msbuild-integration)
 - Then in the sDNA repo's root call `build_release.bat` which should do what it says on the tin.

#### CI build and test requirements:
* Run the Github Action `.github\workflows\compile_and_test.yml`

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
   
