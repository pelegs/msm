#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import simulate, zero_potential
import numpy as np
from scipy.stats import linregress

# CL arguments
D_val = float(sys.argv[1])
num_steps = int(sys.argv[2])
num_dim = int(sys.argv[3])
num_particles = int(sys.argv[4])

# Potential
U = zero_potential()

# Simulation Parameters
parameters = {
    'name': 'MSD_test',
    'num_steps': num_steps,
    'num_dim': num_dim,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': D_val,
    'x0': 0.0,
    'potential': U
}

# Simulation
print('Simulating.')
print('# Steps =', num_steps)
print('# Dimensions =', num_dim)
print('# Particles =', num_particles)
xs = simulate(parameters)

# Calculate MSD
xs_sqr = xs**2
xs_dist_sqr = np.sum(xs**2, axis=1)
MSD = np.mean(xs_dist_sqr, axis=1)

# Analysis
ts = np.linspace(0, num_steps-1, num_steps)
m, b, r, _, e = linregress(ts, MSD)

# Output
with open('data/MSD_D_{:0.2f}.data'.format(D_val), 'w') as f:
    f.write('{} {} {} {} {}\n'.format(D_val, m, b, r, e))
