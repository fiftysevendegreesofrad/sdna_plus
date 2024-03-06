import sys,os

#  On Python 2 and earlier
if sys.version_info.major <= 2:
    encoding = sys.getfilesystemencoding()
    path = os.path.dirname(unicode(__file__, encoding))
else: 
      # On Python 3 there is (and it can be assumed 
      # in all future versions there will be) 
      # native unicode support
    path = os.path.dirname(__file__)


parentdir = os.path.dirname(path)
if parentdir not in sys.path:
    sys.path.insert(0,parentdir)
