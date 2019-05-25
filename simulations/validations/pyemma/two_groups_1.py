#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

import sys
home = '/home/psapir'
sys.path.append('{}/prog/msm/lib'.format(home))
import numpy as np
from simlib import *


gaussians = []

# Group 1
gaussians.append(gaussian(
	A=np.ones(2),
    M=np.array([-4,2]),
    S=np.ones(2)))
gaussians.append(gaussian(
	A=np.ones(2),
    M=np.array([-4,-2]),
    S=np.ones(2)))

# Group 2
gaussians.append(gaussian(
	A=np.ones(2),
    M=np.array([4,2]),
    S=np.ones(2)))
gaussians.append(gaussian(
	A=np.ones(2),
    M=np.array([4,-2]),
    S=np.ones(2)))

parameters = {
    'name': 'equilibrium_test',
    'num_steps': 5000000,
    'num_dim': 2,
    'num_particles': 4,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': np.array([[-4,-4,4,4],
                    [-2,2,-2,2]]),
    'potential': potential(gaussians)
}

Xs = simulate(parameters)
Xs_all = np.vstack((X[:,:,0], Xs[:,:,1], Xs[:,:,2], Xs[:,:,3]))
np.save('Xs_two_groups_1', Xs_all)
