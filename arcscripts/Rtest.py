import sys
import arcpy

arcpy.AddMessage(sys.executable)

import ctypes

arcpy.AddMessage(ctypes.sizeof(ctypes.c_void_p))

import subprocess
cmd = r"d:\sdna\arcscripts\rportable\R-Portable\App\R-Portable\bin\RScript.exe --no-site-file --no-init-file --no-save --no-environ --no-init-file --no-restore --no-Rconsole test.R"
process = subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE) 
stdout,stderr = process.communicate()

def output(x):
    for line in x.split("\n"):
        arcpy.AddMessage(x)

output(stdout)
output(stderr)
    