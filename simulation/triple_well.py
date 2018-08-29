#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Potential
g0 = gaussian()
g1 = gaussian(center=-7.0)
g2 = gaussian(center=+7.0)
u = potential(gaussians=[g0, g1, g2])

# Particles
particles = [particle() for _ in range(num_particles)]

# Simulation
run_simulation(particle_list=particles,
               potential=u,
               t_max=max_t,
               drift=True,
               noise=True,
               name=name)
