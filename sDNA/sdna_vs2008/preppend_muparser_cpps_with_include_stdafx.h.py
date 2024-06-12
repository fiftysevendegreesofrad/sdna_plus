import os
import glob
import tempfile
import shutil

MUPARSER_DIRS = ['muparser', 'drop', 'src']

TMP_DIR = os.path.join(tempfile.gettempdir(), 'sdna_plus_src_backup', *MUPARSER_DIRS)


if not os.path.isdir(TMP_DIR):
    os.makedirs(TMP_DIR)


MUPARSER_SRC_DIR =  os.path.join(os.path.dirname(os.path.dirname(__file__)), *MUPARSER_DIRS)
files_glob = os.path.join(MUPARSER_SRC_DIR, 'muParser*.cpp')

PREFIX = '#include "stdafx.h"'

prepended = False


for file_ in glob.glob(files_glob):
    
    with open(file_, 'rt') as f:
        content = f.read()

    if not content.starts_with(PREFIX):
        content =  PREFIX + content

    with open(file_, 'wt') as f:
        f.write(content)


    prepended = True


if not prepended:
    raise Exception('No files found to change.  files_glob: %s, __file__: %s,' % (files_glob, __file__))