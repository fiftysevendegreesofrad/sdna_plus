import os
import sys
import ctypes

if sys.platform=='win32':
    load_library = ctypes.windll.LoadLibrary
else:
    load_library = ctypes.cdll.LoadLibrary

try:
    import sDNA.sdnapy
except ImportError:
    pass
else:
    ON_WINDOWS = (sys.platform == 'win32')
    LIB_EXT = 'dll' if ON_WINDOWS else 'so'
    os.environ['sdnadll'] = os.path.join(os.path.dirname(sDNA.sdnapy.__file__), 'x64', 'sdna_vs2008.' + LIB_EXT)
