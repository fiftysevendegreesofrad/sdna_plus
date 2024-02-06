import sys
import filecmp

file_1, file_2 = sys.argv[1:3]

if filecmp.cmp(file_1, file_2, shallow=False):
    print(r'[92mPass[0m')
else:
    print(r'[101mTEST FAILED[0m')