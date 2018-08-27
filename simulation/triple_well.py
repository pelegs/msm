#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

# Potential
g0 = gaussian()
g1 = gaussian(center=-3.0)
g2 = gaussian(center=+3.0)
u = potential(gaussians=[g0, g1, g2])

# Particles
num_particles = int(sys.argv[2])
particles = [particle() for _ in range(num_particles)]

# Time
t_max = int(sys.argv[3])

# Simulation
run_simulation(particle_list=particles,
               potential=u,
               t_max=t_max,
               drift=True,
               noise=True,
               name=sys.argv[1])
