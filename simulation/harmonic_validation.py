#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
from simlib import *


method = sys.argv[1]
k = float(sys.argv[2])
D = float(sys.argv[3])
beta = float(sys.argv[4])
x0 = float(sys.argv[5])

num_particles = 100000
max_t = 10
dt = 0.001
num_steps = int(max_t/dt)

print_simulate('harmonic_validation', harmonic_potential(k=k), method=method, num_particles=num_particles, dt=dt, max_t=max_t, x0=x0, D=D, beta=beta)
