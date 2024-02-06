rem test python2 and python3 in turn

@REM set pythonexe=%python2exe%
@REM set outputsuffix=py2

@REM cmd /C run_debug_test.bat

set pythonexe=%python3exe%
set outputsuffix=py3

cmd /C run_debug_test.bat

rem Python 3 test only for the following:
%pythonexe% -u debug_test.py >testout_%outputsuffix%.txt 2>&1
@REM python colourdiff.py correctout.txt testout_%outputsuffix%.txt 
@REM %pythonexe% -u hybrid_test.py >hybrid_testout.txt 2>&1
@REM python colourdiff.py hybrid_correctout.txt hybrid_testout.txt 
@REM %pythonexe% -u 3d_test.py >testout3d_%outputsuffix%.txt 2>&1
@REM python colourdiff.py correctout3d.txt testout3d_%outputsuffix%.txt 
@REM %pythonexe% -u partial_test.py >testout_partial_%outputsuffix%.txt 2>&1
@REM python colourdiff.py correctout_partial.txt testout_partial_%outputsuffix%.txt 
@REM %pythonexe% -u test_parallel_results.py >NUL
@REM %pythonexe% -u prepare_barns_test.py >testout_prepbarns_%outputsuffix%.txt 2>&1
@REM python colourdiff.py correctout_prepbarns.txt testout_prepbarns_%outputsuffix%.txt 

@REM pause