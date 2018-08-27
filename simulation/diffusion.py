#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Potential
g0 = gaussian(center=-2.0)
g1 = gaussian(center=+2.0)
u = potential(gaussians=[g0, g1])

# Particles
num_particles = int(sys.argv[1])
particles = [particle() for _ in range(num_particles)]

# Time
t_max = int(sys.argv[2])

# Simulation
run_simulation(particle_list=particles,
               potential=u,
               t_max=t_max,
               drift=True,
               noise=True,
               name='diffusion')
