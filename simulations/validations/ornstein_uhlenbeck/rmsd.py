#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import *
import numpy as np
from sklearn.metrics import mean_squared_error


# CL arguments
num_steps = int(sys.argv[1])
num_particles = int(sys.argv[2])

# Potential
g = gaussian(A = np.array([1]),
             M = np.array([0]),
             S = np.array([1]))
U = potential([g])

# Parameters
parameters = {
    'name': 'OU_RMSD',
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': 1.5,
    'potential': U
}

# Theory
ts = np.arange(0, num_steps*0.01, 0.01)
mean_theory = 1.5 * np.exp(-ts)
var_theory = 1-exp(-2*ts)

# Simulation
xs = simulate(params=parameters).reshape((num_steps, num_particles))

# Mean, var
mean_sim = np.mean(xs, axis=1)
var_sim = np.var(xs, axis=1)

# RMSD
rmsd_mean = mean_squared_error(mean_sim, mean_theory)
rmsd_var = mean_squared_error(var_sim, var_theory)

# Save data
with open('data/RMSD_{}.data'.format(num_particles), 'w') as f:
    f.write('{} {} {}\n'.format(num_particles, rmsd_mean, rmsd_var))
