#!/usr/bin/env python3
import numpy as np
import sys
sys.path.append('../lib')
from simlib import *


method = sys.argv[1]
num_particles = 1000000
max_t = 10
dt = 0.1
x0 = 2
D = 1.0
beta = 1
k = 0.5
num_steps = int(max_t/dt)

ts, xs = simulate(harmonic_potential(k=k), method=method, num_particles=num_particles, dt=dt, max_t=max_t, x0=x0, D=D, beta=beta)

m = np.mean(xs, axis=1)
v = np.var(xs, axis=1)
dm = np.std(xs, axis=1) / np.sqrt(num_particles)
dv = 2/(num_particles-1)*v**2

with open('../data/harmonic_validation_{}.data'.format(method), 'w') as f:
    f.write('# num particles: {}, D={}, beta={}, k={}\n'.format(num_particles, D, beta, k))
    for i, t in enumerate(ts):
        f.write('{} {} {} {} {}\n'.format(t, m[i], dm[i], v[i], dv[i]))
