import sys
import ctypes

if sys.platform=='win32':
    load_library = ctypes.windll.LoadLibrary
else:
    load_library = ctypes.cdll.LoadLibrary
