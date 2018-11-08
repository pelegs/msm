#!/usr/bin/env python3

import numpy as np
from tqdm import tqdm

import sys
sys.path.append('../lib')
from simlib import *

g1 = gaussian(-3)
g2 = gaussian(+3)
U = gaussian_potential([g1, g2])

ts, xs, _, _ = simulate(U, method='langevin', num_particles=1, max_t=5000, x0=0, D=0.5, num_bins=50)

with open('static_gaussian_langevin.data', 'w') as f:
    for b, h in zip(hist[-1], bin_edges):
        f.write('{} {}\n'.format(b, h))
