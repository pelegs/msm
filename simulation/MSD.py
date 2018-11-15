#!/usr/bin/env python3

import numpy as np
from scipy import stats
import sys

sys.path.append('../lib')
from simlib import *


def MSD(xs):
    return np.array([np.mean(np.array([[(xs[t,i]-xs[0,i])**2 for t, _ in enumerate(xs)]
                                                    for i, _ in enumerate(xs[0,:])])[:,j])
            for j, _ in enumerate(xs)])


method = sys.argv[1]
num_particles = 10000

Ds = np.arange(0.1, 5.0, 0.1)
dt = 0.1
max_t = 10
steps = int(max_t/dt)

ts = len(Ds)*[0]
xs = len(Ds)*[0]

ms = []
covs = []
for i, D in enumerate(Ds):
    ts[i], xs[i]= simulate(zero_potential(), method=method, num_particles=num_particles, D=D, max_t=max_t, dt=dt)
    m, cov = np.polyfit(ts[i], MSD(xs[i]), 1, cov=True)
    ms.append(m[0])
    covs.append(np.sqrt(np.diag(cov))[0])

with open('../data/MSD_{}.data'.format(method), 'w') as f:
    for D, m, err in zip(Ds, ms, covs):
        f.write('{} {} {}\n'.format(2*D, m, err))
