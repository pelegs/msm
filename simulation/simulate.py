#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Potential
gs = parse_gaussians(name)
u = potential(gaussians=gs)

# Particles
particles = [particle() for _ in range(num_particles)]

# Simulation
run_simulation(particle_list=particles,
               potential=u,
               t_max=max_t,
               drift=True,
               noise=True,
               name=name)
