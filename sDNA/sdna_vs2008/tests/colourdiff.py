import sys
import filecmp

# import os
# import tempfile
# import subprocess


file_1, file_2 = sys.argv[1:3]


# SDNA_DEBUG = bool(os.getenv('sdna_debug', ''))


# if not SDNA_DEBUG:
#     TMP_SDNA_DIR = os.path.join(tempfile.gettempdir(), 'sDNA', 'tests', 'filtered_correctouts')

#     if not os.path.isdir(TMP_SDNA_DIR):
#         os.makedirs(TMP_SDNA_DIR)

#     if 'correctout' in file_2:
#         file_1, file_2 = file_2, file_1

#     tmp_file_name = os.path.join(TMP_SDNA_DIR, os.path.basename(file_1))

#     tmp_file_name = os.path.splitext(tmp_file_name)[0] + '_filtered_no_debug_output.txt'

#     script = os.path.join(os.path.dirname(__file__), 'pytest', 'filter_out_debug_only_output.py')

#     subprocess.check_output('python %s %s > %s' % (script, file_1, tmp_file_name))

#     file_1 = tmp_file_name



if filecmp.cmp(file_1, file_2, shallow=False):
    print(r'[92mPass[0m')
else:
    print(r'[101mTEST FAILED[0m')