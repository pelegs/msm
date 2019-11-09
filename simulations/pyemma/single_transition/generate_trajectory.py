#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import numpy as np
import pyemma
import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import *


# Potential
gaussians = []
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([-6,-6]),
                          S=np.array([1.5, 1.5])))
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([0,0]),
                          S=np.ones(2)))
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([1,5]),
                          S=np.ones(2)))
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([5,1]),
                          S=np.ones(2)))
U = potential(gaussians)

# Parameters
parameters = {
    'name': 'equilibrium_test',
    'num_steps': 10000000,
    'num_dim': 2,
    'num_particles': 1,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': np.array([[-6],[-6]]),
    'potential': U,
}

# Simulate
xs = simulate(parameters)

# Save data
np.save('trajectories/single_trajectory_full', xs[:,:,0])
