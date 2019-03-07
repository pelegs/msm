#!/usr/bin/env python3

import numpy as np
from numpy import sqrt, pi, exp, log
sqrt2pi = 1/sqrt(2*pi)


def gaussian(x, a, m, s):
    return a * sqrt2pi/s * exp(-(x-m)**2/(2*s**2))

def discrete_gaussian(a, m, s, xmin, xmax, dx):
    return {x:gaussian(x, a, m, s) for x in np.arange(xmin, xmax, dx)}

ys = discrete_gaussian(1, 0, 1, -5, 5, 0.1)
for x, y in ys.items():
    print(x, y)
