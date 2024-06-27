import sys,os


up = os.path.dirname


arcscriptsdir = ''

# Prioritise testing the Python code shipped with 
# the sDNA installer along with the .dll and .so,
# over the Python code in the dev repo.

try:
    import sDNA
except ImportError:
    sdna_dll_path = os.getenv('sdnadll','')
else:
    arcscriptsdir = up(sDNA.__file__)
    sdna_dll_path = ''
    import load_library

if sdna_dll_path:
    arcscriptsdir = up(up(sdna_dll_path)) 

if not arcscriptsdir or not os.path.isdir(arcscriptsdir):
    path = up(__file__)
    arcscriptsdir = os.path.join(up(up(up(path))), "arcscripts")


if arcscriptsdir not in sys.path:
    sys.path.insert(0,arcscriptsdir)

