#!/usr/bin/env python3

import numpy as np
from pyemma import msm

x = 0.4
m = np.array([[1-2*x, x, x, 0, 0, 0, 0, 0, 0],
              [x, 1-2*x-x/10, x, 0, x/10, 0, 0, 0, 0],
              [x, x, 1-2*x, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 1-2*x, x, x, 0, 0, 0],
              [0, x/10, 0, 1-2*x-x/10-x/10, x, x, 0, x/10, 0],
              [0, 0, 0, x, x, 1-2*x, 0, 0, 0],
              [0, 0, 0, 0, x/10, 0, 1-2*x-x/10, x, x],
              [0, 0, 0, 0, 0, 0, x, 1-2*x, x],
              [0, 0, 0, 0, 0, 0, x, x, 1-2*x]])

print('yeah')
