import sys,os


up = os.path.dirname

sdna_dll = os.getenv('sdnadll','')

arcscriptsdir = ''

if sdna_dll:
    arcscriptsdir = up(up(sdnadll)) 

if not arcscriptsdir or not os.path.isdir(arcscriptsdir):
    path = up(__file__)
    arcscriptsdir = os.path.join(up(up(up(path))), "arcscripts")


if arcscriptsdir not in sys.path:
    sys.path.insert(0,arcscriptsdir)
