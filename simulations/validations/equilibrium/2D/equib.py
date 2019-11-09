#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import *
import numpy as np


# CL arguments
name = sys.argv[1]
id = int(sys.argv[2])
num_particles = int(sys.argv[3])
num_steps = int(sys.argv[4])
t0 = int(sys.argv[5])
Ddt = float(sys.argv[6])

# Other parameters
xmin, xmax = -6, 6

U = potential()
U.load('potentials/{}.pt'.format(name))

# Simulation Parameters
equilibrated_positions = create_starting_positions(U, num_particles, xmin, xmax)
parameters = {
    'name': name,
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': Ddt,
    'x0': equilibrated_positions,
    'potential': U
}

# Simulation
xs = simulate(parameters)

# Truncate
xs_trunc = xs[t0:].reshape((num_steps-t0, num_particles))

# Save
np.save('data/equib_1D_{}_id{}.npy'.format(name, id), xs_trunc)
