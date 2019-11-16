#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import *
import numpy as np
#from sklearn.metrics import mean_squared_error as MSE


# CL arguments
id = int(sys.argv[1])
num_steps = int(sys.argv[2])
Ddt = float(sys.argv[3])
beta = float(sys.argv[4])
x0 = float(sys.argv[5])

# Number of particles
Ns = np.linspace(100, 10000, 200).astype(int)
num_particles = Ns[id-1]

# Potential
g = gaussian(A=np.array([1]),
             M=np.array([0]),
             S=np.array([1]))
U = potential([g], kBT=1.0/beta)

# Simulation Parameters
parameters = {
    'name': 'OU_RMSD',
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': num_particles,
    'kBT': 1.0/beta,
    'Ddt': Ddt,
    'x0': np.ones(num_particles)*x0,
    'potential': U
}

# Simulation
xs = simulate(parameters).reshape((num_steps, num_particles))

# "RMSD"
ts = np.arange(0, Ddt*num_steps, Ddt)
mean_theory = x0 * np.exp(-beta * ts)
mean_sim = np.mean(xs, axis=1)
diff = np.abs(mean_theory - mean_sim)
data = np.c_[ts, mean_theory, mean_sim, diff]

# Save
np.save('data/ou_b{:0.2f}_N{}.data'.format(beta, num_particles), data)
