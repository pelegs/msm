#!/usr/bin/env python3

import numpy as np
from tqdm import tqdm

import sys
sys.path.append('../lib')
from simlib import *

ks = [0.5, 1.0, 1.5, 2.0, 2.5]
bs = [0.1, 0.3, 0.7, 1.0, 1.2]
sqrtbks = []

times, positions = [], []
for k in tqdm(ks):
    for b in tqdm(bs):
        sqrtbks.append(1/np.sqrt(b*k))
        U = harmonic_potential(k=k)
        ts, xs, _, _ = simulate(U, method='smol', num_particles=1, max_t=100000, x0=0, D=0.5, KT=1/b)
        times.append(ts)
        positions.append(xs)

stdevs, means = [], []
for xs in tqdm(positions):
    mean = np.mean(xs[100:-1,0])
    stdev = np.std(xs[100:-1,0])
    means.append(mean)
    stdevs.append(stdev)

with open('../data/static_harmonic_smol.data', 'w') as f:
    for kb, mean, stdev in zip(sqrtbks, means, stdevs):
        f.write('{} {} {}\n'.format(kb, mean, stdev))
