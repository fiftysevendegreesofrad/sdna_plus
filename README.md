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

Soon to be hosted on readthedocs.

### Support

Please see the original project [support page](https://www.cardiff.ac.uk/sdna/support/).

If filing a bug, please file to the database here on github. 

## For Developers

### Building the software

Build requirements:

* Microsoft Visual Studio (tested on 2022) with C++ extensions
* Python 2.7
* Advanced Installer

Fire up the Visual Studio Developer Command Prompt. Then call `build_release.bat` in project root which should do what it says on the tin.

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

For testing the core network processing and numerical routines, fire up the `sdna_vs2008.sln` solution in `sDNA\sDNA_vs2008`. 
You will need the correct debug settings; unfortunately Visual Studio stores these with user information. Copy `sdna\sdna_vs2008\sdna_vs2008.vcproj.octopi.Crispin.user.sample` on top of your own `sdna_vs2008.vcproj.yourmachine.yourusername.user` file.
Set build configuration to `Debug Win32`, and run. This calls scripts in `sDNA\sDNA_vs2008\tests` and diffs the output with correct outputs (the core of which are originally hand computed) in that directory. Any call to `diff` that shows differences is a test fail.

For `test_parallel_results.py` to work, you also need to build the `parallel_debug Win32` configuration. When `Debug Win32` is run as described above, serial and parallel results are compared to check they are identical.

Interfaces are not automatically tested, though `arcscripts\sdna_environment.py` can be tested by `environment_test.py`.

## License

The bulk of sDNA+ is licensed under GNU Affero v3, with various other Free licenses for various modules. For full details see [licensing](LICENSE.md).
   