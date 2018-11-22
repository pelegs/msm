#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
from tqdm import tqdm
from simlib import *


#method = sys.argv[1]
#k = float(sys.argv[2])
#D = float(sys.argv[3])
#beta = float(sys.argv[4])
#x0 = float(sys.argv[5])
#
#num_particles = int(sys.argv[6])
#max_t = float(sys.argv[7])
#dt = float(sys.argv[8])
#num_steps = int(max_t/dt)

Ds = [1.0, 1.2]
ks = [1.0, 1.3]
betas = [1.0, 1.5]

method = sys.argv[1]
num_particles = int(sys.argv[2])
dt = float(sys.argv[3])
max_t = float(sys.argv[4])

print_simulate('harmonic_validation', harmonic_potential(k=ks[0]),
                method=method, num_particles=num_particles, dt=dt,
                max_t=max_t, x0=2, D=Ds[0], beta=betas[0])
