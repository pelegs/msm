#!/usr/bin/env python2.7
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
import numpy as np
import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib_27 import *


# CL parameters
m = float(sys.argv[1])
num_steps = int(sys.argv[2])

# Potential parameters
g1 = gaussian(np.ones(1),
              np.array([-m]),
              np.array([1]))
g2 = gaussian(np.ones(1),
              np.array([m]),
              np.array([1]))
gaussians = [g1, g2]
U = potential(gaussians)

# Other parameters
parameters = {
    'name': 'equilibrium_test',
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': 1,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': -m,
    'potential': U
}

# Simulation
xs = simulate(parameters)

# Save data
np.save('data/kramers_{}.npy'.format(m), xs)
