import sys

import _parentdir
from commandline_integral_prepare import commandline_integral_prepare

def main(argv = sys.argv[1:]):
    commandline_integral_prepare("sdnaprepare", argv)
    return 0

if __name__ == '__main__':
    main()
    
