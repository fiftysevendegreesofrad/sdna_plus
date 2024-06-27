import sys

from .bin import (sdnaintegral,
                  sdnalearn,
                  sdnapredict,
                  sdnaprepare
                 )

scripts = dict(integral=sdnaintegral,
               learn = sdnalearn,
               predict = sdnapredict,
               prepare = sdnaprepare,
              )

def main(args = sys.argv[1:]):
    return scripts[args[0].lower()].main(args[1:])


if __name__ == '__main__':
    main()