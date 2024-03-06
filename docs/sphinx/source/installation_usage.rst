.. include:: <isonum.txt>

.. _`installation and first usage`:

****************************
Installation and first usage
****************************

Requirements
************

sDNA requires Windows XP or later.  We suggest a minimum of 1GB RAM, but obviously faster computers and more memory will be of use in analyzing larger networks.  sDNA can run in 32- or 64-bit mode depending on the host application.

The toolbox can be used in any of a number of ways:

-  As a plug-in to ArcGIS 10.1 or later, or

-  As a plug-in to ArcGIS Professional, or

-  As a plug-in to QGIS 2.0 or later, or

-  From the windows command line, or

-  From sdnapy, the python API to sDNA.

Installation
************

sDNA can be downloaded an installed from our website_.  

.. _website: http://sdna.cardiff.ac.uk/sdna/software/download/

Further steps are then needed depending on how you plan to use sDNA.

How you use sDNA depends on your host application.

ArcGIS 10.x
===========

1. From inside ArcGIS, go to ArcToolbox.

2. Right click the root of the ArcToolbox tree and choose ``Add
   Toolbox...``".

3. Navigate to the place you have installed sDNA (usually ``c:\Program
   Files (x86)\sDNA``) and select the toolbox ``sdna.pyt``.
   
4. (Optional) Repeat steps 2 and 3 to add the toolbox ``sDNA_ArcGIS_extra_tools.tbx``.

5. (Optional) To permanently add sDNA to ArcToolbox, right click the
   root of ArcToolbox and choose ``Save settings`` |rarr| ``to Default``.

sDNA appears as a set of tools within ArcToolbox. Results can be
displayed using the ``Symbology`` tab of the ``Layer Properties``
dialog. If you are not familiar with using tools from ArcToolbox, or
changing layer symbology, visit the *ArcGIS Desktop Help* website for
further details.

ArcGIS Professional
===================

In ArcGIS Professional, external toolboxes appear in the Catalog rather than with ESRI's own geoprocessing tools.

1. From inside ArcGIS, navigate to the "View" ribbon and choose "Catalog Pane" to open the catalog.

2. In the Catalog pane, right click on "Toolboxes", Choose "Add Toolbox"

3. Navigate to the place you have installed sDNA (usually ``c:\Program
   Files (x86)\sDNA``) and select the toolbox ``sdna.pyt``.

The tools can then be used from the catalog. 

QGIS
====

1. From inside QGIS, choose ``Plugins`` |rarr| ``Manage and install plugins...``.  At present, QGIS support is considered experimental, so go to ``Settings`` and click ``Also show experimental plugins``.

2. Type "sdna" into the search box; you should find the Spatial Design Network Analysis plugin. Different sDNA plugins should appear depending on which version of QGIS you are using (2 or 3).

3. Click ``Install Plugin``, then ``Close``

4. Go to ``Processing`` |rarr| ``Toolbox`` to show the processing toolbox

5. At the bottom of the processing toolbox, change from ``Simplified interface`` to ``Advanced interface``

6. "Spatial Design Network Analysis" should now appear in the processing toolbox

7. Go to ``Processing`` |rarr| ``Options`` |rarr| ``General`` and ensure ``Keep dialog open after running an algorithm`` is switched on.

Results of sDNA operations can be displayed using layer styles.  After running sDNA, right-click the relevant layer in the layers panel, choose ``Properties`` |rarr| ``Style``, change ``Single Symbol`` to ``Graduated`` and select the data you want to display.

Advanced sDNA models in Autocad Map3d
=====================================

The Autocad interface to sDNA has been sunsetted as of 2024, as vanilla Autocad did not support field data essential to most users of sDNA.

To use sDNA from Autocad Map3d, we recommend the following workflow:

1. Export data as a shapefile.
2. Process in the free QGIS_ or by `using sDNA from the command line`_.
3. Re-import into Map3d.

This enables the use of Map3d's sophisticated 3d editing and snapping features in sDNA models.  However, please take note of the following:

* Do not edit shapefiles as a Map3d mapping layer, as this discards 3d information.  
* Instead, create your network using Autocad polylines.  
* Models can be exported from Autocad polylines to shapefiles.  Note that (1) it is necessary to manually specify export of all attached object data, (2) it is necessary to select the 3d export driver to preserve height data, and (3) care must be taken to preserve the spatial referencing.
* Shapefiles can be imported into Map3d as Autocad objects, with data attached as object data, and preserving spatial reference. 
   
.. _command line:   

Using sDNA from the command line
================================

sDNA can also be used to process shapefiles from the command line. 
Before starting, you will need to install Python, if you don’t have it
already. We have tested with versions 2.6 and 2.7; other versions may
work as well. You can download Python 2.7.3 from here_:

.. _here: http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi

If your file associations are set up correctly for python (the python
installer should have done this) and the sDNA bin directory (usually
``c:\program files\sdna\bin``) has been added to your path (the sDNA
installer should have done this), then you can use command line sDNA as
follows.

The commands are ``sdnaprepare.py``, ``sdnaintegral.py``, ``sdnalearn.py`` and ``sdnapredict.py``.  Note that from the command line, various functions handled separately in QGIS and ArcGIS (geodesics, convex hulls, link measures, destination maps, network radii) are all handled by ``sdnaintegral.py``.  See :ref:`advanced_config` for more details; alternatively to learn the command for a given operation, try performing the operation from QGIS and see the command QGIS calls (shown in the algorithm dialog).

If you have ArcGIS 10.1 or later installed, then the command line
interface to sDNA will also support work on geodatabase paths. Of course
you can use sDNA from inside ArcGIS as well, but some of us like to make
batch scripts to run outside of Arc. 

Troubleshooting
---------------

If you haven't, can't or don't want to set up file associations, then
the instructions above won’t work. You will have to load python
explicitly, e.g. (assuming python is on your system path):

``python -u sdnaprepare.py --help``

(or if it isn't):

``c:\path\to\python -u sdnaprepare.py --help``

(or if neither python nor the sdna bin folder are on your path)

``c:\path\to\python -u c:\path\to\sdna\bin\sdnaprepare.py
–help``

and so on, for the other sDNA commands detailed above.

Using sDNA through the Python interface
=======================================

Those experienced in programming may want to use sDNA Prepare and sDNA Integral directly through our Python API.
This is called ``sdnapy``; the canonical example of its use can be found in ``runcalculation.py`` in the sDNA program folder.

