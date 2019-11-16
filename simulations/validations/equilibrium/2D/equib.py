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

U = potential()
U.load('potentials/{}.pt'.format(name))

# Simulation Parameters
parameters = {
    'name': name,
    'num_steps': num_steps,
    'num_dim': 2,
    'num_particles': num_particles,
    'kBT': 1,
    'Ddt': Ddt,
    'x0': np.random.uniform(-7, 7, size=(2, num_particles)),
    'potential': U
}

# Simulation
xs = simulate(parameters)

# Save
np.save('data/equib_2D_{}_id{}.npy'.format(name, id), xs)
