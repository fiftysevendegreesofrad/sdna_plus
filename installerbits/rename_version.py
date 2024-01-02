import os,re,sys,_parentdir,shutil
from getSdnaVersion import getVersion

installfile,outputdir = sys.argv[1:3]

print installfile
print outputdir

version = getVersion()

filename_friendly_version = re.sub("\.","_",version)

outfilename = "%s/sDNA_setup_win_v%s.msi"%(outputdir,filename_friendly_version)

if (os.path.exists(outfilename)):
    os.unlink(outfilename)
    
os.rename(installfile,outfilename)
