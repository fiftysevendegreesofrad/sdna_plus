from sdnaregutilities import *
import numpy

def simdata():
    xs = numpy.arange(30)
    ys = xs + 5*numpy.sin(xs)
    return xs,ys

xs,ys = simdata()
print('''
0.925476862734
(0.9802520605214966, 0.49769211916578016)
''')

print(pearson_r(xs,ys,[1 for x in xs]))
print(univar_regress(xs,ys,[1 for x in xs]))
