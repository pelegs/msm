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
Ddt = float(sys.argv[5])

# Other parameters
xmin, xmax = -5, 5
#num_bins = 1000
#tbins = np.linspace(xmin, xmax, num_bins)

U = potential()
U.load('potentials/{}.pt'.format(name))

# Simulation Parameters
parameters = {
    'name': name,
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': num_particles,
    'kBT': 1,
    'Ddt': Ddt,
    'x0': np.random.uniform(xmin, xmax, num_particles),#create_equilibrium_positions(U, tbins, num_particles),
    'potential': U
}

# Simulation
xs = simulate(parameters)

# Save
np.save('data/equib_1D_{}_id{}.npy'.format(name, id), xs)
