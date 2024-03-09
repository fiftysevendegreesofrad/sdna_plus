from __future__ import print_function

import os,re,sys,_parentdir,shutil
from getSdnaVersion import getVersion

installfile,outputdir = sys.argv[1:3]

print(installfile)
print(outputdir)

version = getVersion()

filename_friendly_version = re.sub(r"\.","_",version)

outfilename = os.path.join(outputdir, "sDNA_setup_win_v%s.msi" % filename_friendly_version)

if (os.path.exists(outfilename)):
    os.unlink(outfilename)
    
os.rename(installfile,outfilename)
