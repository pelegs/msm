#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
from simlib import *

method = sys.argv[1]

ks = [0.5, 0.7, 0.9, 1.0, 2.0, 3.0]
bs = [0.1, 0.3, 0.5, 0.7, 1.0, 1.5]
Us = []

dt = 0.1
max_t = 1
steps = int(max_t/dt)

ts = 6*[0]
xs = 6*[0]

for (i, b), k in zip(enumerate(bs), ks):
    ts[i], xs [i]= simulate(harmonic_potential(k=k), method=method, num_particles=10000, x0=2, D=1, KT=1/b, max_t=max_t)

with open('../data/harmonic_{}.data'.format(method), 'w') as f:
    for i, t in enumerate(ts[0]):
        means = ' '.join(map(str, [np.mean(x[i,:]) for x in xs]))
        stdevs = ' '.join(map(str, [np.std(x[i,:]) for x in xs]))
        f.write('{} {} {}\n'.format(t, means, stdevs))
