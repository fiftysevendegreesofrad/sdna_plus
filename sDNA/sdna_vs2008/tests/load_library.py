import os
import sys
import ctypes

if sys.platform=='win32':
    _load_library = ctypes.windll.LoadLibrary
else:
    _load_library = ctypes.cdll.LoadLibrary

try:
    import sDNA
except ImportError as e:
    load_library = _load_library
    raise e
else:
    ON_WINDOWS = (sys.platform == 'win32')
    LIB_EXT = 'dll' if ON_WINDOWS else 'so'
    installed_dll = os.path.join(os.path.dirname(sDNA.__file__), 'x64', 'sdna_vs2008.' + LIB_EXT)
    os.environ['sdnadll'] = installed_dll
    def load_library(ignored_dll):
        return _load_library(installed_dll)
