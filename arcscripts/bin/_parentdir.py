# sDNA+ (c) Crispin Cooper on behalf of Cardiff University 2015

__version__ = "VERSION_PLACEHOLDER"

import sys,os

encoding = sys.getfilesystemencoding()
# path = os.path.dirname(str(__file__, encoding))  # TODO
path = os.path.dirname(str(__file__))
parentdir = os.path.dirname(path)
if parentdir not in sys.path:
    sys.path.insert(0,parentdir)
