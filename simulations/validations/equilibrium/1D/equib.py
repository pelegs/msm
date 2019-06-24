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
g1 = gaussian(np.ones(1),
              np.array([-6]),
              np.array([1]))
g2 = gaussian(np.ones(1)*2,
              np.array([2]),
              np.array([1]))
g3 = gaussian(np.ones(1)*3,
              np.array([7]),
              np.array([1]))
gaussians = [g1, g2, g3]
U = potential(gaussians)

# Other parameters
x0s = create_starting_positions(U, xmin=-13, xmax=13, num_particles=num_particles)
parameters = {
    'name': 'equilibrium_test',
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': x0s,
    'potential': U
}

# Simulation
xs = simulate(parameters)

# Reshape xs array
xs_all = np.zeros(1)
for i in range(num_particles):
    xs_all = np.vstack((xs_all, xs[:,:,i]))

# Histogram
bins = np.linspace(-13, 13, 200)
hist, _ = np.histogram(xs_all[:,0], bins)

# Save data
np.save('data/hist_{}.npy'.format(id), hist)
