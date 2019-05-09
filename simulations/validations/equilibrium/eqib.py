#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

from pathlib import Path
home = str(Path.home())
import sys
sys.path.append('{}/prog/msm/lib'.format(home))

import numpy as np
from simlib import *

N = 20
gaussians = [gaussian(A = np.ones(2),
                      M = np.random.uniform(-10,10,size=2),
                      S = np.random.uniform(0.5,2.5,size=2))
             for _ in range(N)]
x = np.arange(-10, 10, 0.1)
y = np.arange(-10, 10, 0.1)
xx, yy = np.meshgrid(x, y, sparse=True)
z = np.sum(g.get_value([xx, yy]) for g in gaussians)
np.save('z.npy', z)

M = 1
parameters = {
    'name': 'equilibrium_test',
    'num_steps': 500000,
    'num_dim': 2,
    'num_particles': M,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': np.random.uniform(-5,5,M),
    'potential': potential(gaussians)
}

Xs = simulate(parameters)

t = parameters['num_steps']
d = parameters['num_dim']
n = parameters['num_particles']
Xs_all = Xs.reshape((t, d*n))


np.save('Xs_all.npy', Xs_all)
