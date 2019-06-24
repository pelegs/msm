#!/usr/bin/env python2.7
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
import numpy as np
import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib_27 import *


# CL parameters
id = int(sys.argv[1])
num_particles = int(sys.argv[2])
num_steps = int(sys.argv[3])

# Potential parameters
g1 = gaussian(np.ones(2),
              np.array([0,0]),
              np.array([2,1]))
g2 = gaussian(np.ones(2),
              np.array([-2,2]),
              np.array([1,2]))
g3 = gaussian(np.ones(2),
              np.array([3,-3]),
              np.array([1,1]))
gaussians = [g1, g2, g3]

# Other parameters
x0s = np.random.uniform(-6, 6, size=(2, num_particles))
parameters = {
    'name': 'equilibrium_test',
    'num_steps': num_steps,
    'num_dim': 2,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': x0s,
    'potential': potential(gaussians)
}

# Simulation
xs = simulate(parameters)

# Reshape xs array
xs_all = np.empty(2)
for i in range(num_particles):
    xs_all = np.vstack((xs_all, xs[:,:,i]))

# Histogram
xbins = np.linspace(-10, 10, 75)
ybins = np.linspace(-10, 10, 75)
hist, _, _ = np.histogram2d(xs_all[:,0], xs_all[:,1], bins=(xbins, ybins))

# Save data
with open('data/eq2d_{}.data'.format(id), 'w') as f:
    for row in xs_all:
        f.write(' '.join(map(str, row)) + '\n')
