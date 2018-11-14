#!/usr/bin/env python3

import numpy as np
from tqdm import tqdm

import sys
sys.path.append('../lib')
from simlib import *

method = sys.argv[1]

ks = [0.5, 1.0, 1.5, 2.0, 2.5]
bs = [0.1, 0.3, 0.7, 1.0, 1.2]
sqrtbks = []

times, positions = [], []
for k in tqdm(ks):
    for b in tqdm(bs):
        sqrtbks.append(1/np.sqrt(b*k))
        U = harmonic_potential(k=k)
        ts, xs = simulate(U, method=method, num_particles=1000, max_t=10000, x0=2, D=1, KT=1/b)
        times.append(ts)
        positions.append(xs)

stdevs, means = [], []
for xs in tqdm(positions):
    mean = np.mean(xs[1000:-1,0])
    stdev = np.std(xs[1000:-1,0])
    means.append(mean)
    stdevs.append(stdev)

with open('../data/static_harmonic_{}.data'.format(method), 'w') as f:
    for kb, mean, stdev in zip(sqrtbks, means, stdevs):
        f.write('{} {} {}\n'.format(kb, mean, stdev))
