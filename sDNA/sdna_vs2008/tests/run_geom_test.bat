@echo off

echo running shape tests

del tinyout*
del geom_test_%outputsuffix%.txt

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_1_10_cont_%outputsuffix% --dll %sdnadll% "metric=EUCLIDEAN;outputgeodesics;nonetdata;radii=350;origins=1;destinations=10;cont" >geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_12_47_bothends_strict_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputgeodesics;nonetdata;radii=350;origins=12;destinations=47;cont" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_12_47_bothends_nonstrict_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputgeodesics;nonetdata;radii=350;origins=12;destinations=47;cont;nostrictnetworkcut" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_originfrommiddle_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputdestinations;nonetdata;radii=100;origins=3;destinations=3;cont" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_all_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputdestinations;outputnetradii;outputgeodesics;outputhulls;nonetdata;radii=5,300,n;origins=16;cont" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_radmetcomp_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputgeodesics;nonetdata;radii=200;origins=16" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_radmeteucsim_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputgeodesics;nonetdata;radii=400;origins=16;radmetric=hybrid;radlineformula=2*LLen*euc/FULLeuc" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_radmet_%outputsuffix% --dll %sdnadll% "metric=ANGULAR;outputgeodesics;nonetdata;radii=200;origins=16;radmetric=hybrid;radjuncformula=ang;radlineformula=ang+euc" >>geom_test_%outputsuffix%.txt 

%pythonexe% -u shp2txt.py tinyout_1_10_cont_%outputsuffix%* tinyout_1_10_disc_%outputsuffix%* tinyout_12_47_bothends_strict_%outputsuffix%* tinyout_12_47_bothends_nonstrict_%outputsuffix%* tinyout_originfrommiddle_%outputsuffix%* tinyout_all_%outputsuffix%* tinyout_radmetcomp_%outputsuffix%* tinyout_radmeteucsim_%outputsuffix%* tinyout_radmet_%outputsuffix%* >testout_geom_%outputsuffix%.txt 

%pythonexe% -u ..\..\..\arcscripts\bin\sdnaintegral.py -i tiny.shp -o tinyout_radmetcont_%outputsuffix% --dll %sdnadll% "cont;metric=ANGULAR;outputgeodesics;nonetdata;radii=200;origins=16;radmetric=hybrid;radjuncformula=ang;radlineformula=ang+euc" >>testout_geom_%outputsuffix%.txt 2>NUL

@echo on

cmd /C mydiff correctout_geom.txt testout_geom_%outputsuffix%.txt



