#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Set file name
sim_name = sys.argv[1]

# Parameters
parameters, gs = parse_parameters_file(sim_name)
u = potential(gaussians=gs)

# Particles
particles = [particle() for _ in range(num_particles)]

# Simulation
run_simulation(sim_name=sim_name,
               particle_list=particles,
               potential=u,
               drift=True,
               noise=True)
