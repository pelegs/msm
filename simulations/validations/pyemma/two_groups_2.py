#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

import sys
home = '/home/psapir'
sys.path.append('{}/prog/msm/lib'.format(home))
import numpy as np
from simlib import *


gaussians = []
m = 8
dm = 1.5
s3_2 = np.sqrt(3)/2*m

# Group 1
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([-m/2,+dm]),
                          S=np.ones(2)))
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([-m/2,-dm]),
                          S=np.ones(2)))

# group 2
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([m/2,+dm]),
                          S=np.ones(2)))
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([m/2,-dm]),
                          S=np.ones(2)))

# group 3
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([+dm, s3_2]),
                          S=np.ones(2)))
gaussians.append(gaussian(A=np.ones(2),
                          M=np.array([-dm,s3_2]),
                          S=np.ones(2)))


parameters = {
    'name': 'equilibrium_test',
    'num_steps': 5000000,
    'num_dim': 2,
    'num_particles': 3,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': np.array([[-m,m,0],
                    [0,0,s3_2]]),
    'potential': potential(gaussians)
}

Xs = simulate(parameters)
Xs_all = np.vstack((Xs[:,:,0], Xs[:,:,1], Xs[:,:,2]))
np.save('Xs_two_groups_2', Xs_all)
