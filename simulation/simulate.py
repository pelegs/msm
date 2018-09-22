#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Set file name
sim_name = sys.argv[1]

# Parameters
parameters, gaussians = parse_parameters_file(sim_name)
u = potential(parameters, gaussians)

# Particles
particles = [particle(parameters) for _ in range(parameters['num_particles'])]

# Simulation
run_simulation(sim_name=sim_name,
               parameters=parameters,
               particle_list=particles,
               potential=u,
               drift=True,
               noise=True)
