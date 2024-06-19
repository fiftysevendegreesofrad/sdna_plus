import sys
import ctypes
import pathlib
import platform


arch = platform.architecture()
print('Architecture: %s' % (arch,))
DIR = 'x86' if arch[0] == '32bit' else 'x64'

paths = [pathlib.Path('%s/src/geos_c.dll' % DIR) ]
for arg in sys.argv[1:]:
    paths.append(pathlib.Path(arg))

for path in paths:
    geos_dll = ctypes.windll.LoadLibrary(str(path.resolve()))
    geos_dll.GEOSversion.restype = ctypes.c_char_p
    print('DLL: %s geos_dll.GEOSversion()=%s' % (path, geos_dll.GEOSversion()))


