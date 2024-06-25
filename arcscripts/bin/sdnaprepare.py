import sys


def main(argv = sys.argv[1:]):
    from commandline_integral_prepare import commandline_integral_prepare
    commandline_integral_prepare("sdnaprepare", argv)
    return 0

if __name__ == '__main__':
    import _parentdir
    main()
else:
    from . import _parentdir
    
