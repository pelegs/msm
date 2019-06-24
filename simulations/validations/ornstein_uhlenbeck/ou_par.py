#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

import numpy as np
import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib_27 import *

g = [gaussian(np.ones(1), np.array([0]), np.ones(1))]

id = int(sys.argv[1])
num_particles = int(sys.argv[2])
num_steps = int(sys.argv[3])

x0 = np.ones(num_particles) * 3
parameters = {
    'name': 'equilibrium_test',
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': x0,
    'potential': potential(gaussians)
}

Xs = simulate(parameters)

with open('data/2D_equib_par_{}.data'.format(id), 'w') as f:
    for x, y in zip(X, Y):
        f.write('{} {}\n'.format(x, y))
