#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Set file name
sim_name = sys.argv[1]

# Parameters
parameters, components = parse_parameters_file(sim_name)
if parameters['potential_type'] == 'gaussian':
    u = gaussian_potential(parameters, components)
elif parameters['potential_type'] == 'harmonic':
    u = harmonic_potential(parameters, components)

# Particles
particles = [particle(parameters) for _ in range(parameters['num_particles'])]

# Simulation
run_simulation(sim_name=sim_name,
               parameters=parameters,
               particle_list=particles,
               potential=u,
               drift=parameters['drift'],
               noise=parameters['noise'])
