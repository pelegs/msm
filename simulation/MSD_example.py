#!/usr/bin/env python3

import numpy as np
from scipy.odr import *

import sys
sys.path.append('../lib')
from simlib import *


def linear_func(B, x):
    return B[0]*x + B[1]


method = sys.argv[1]
num_particles = 10000

err_MSD = 1/np.sqrt(num_particles)
err_VAR = 4/np.sqrt(num_particles-1)

dt = 0.1
max_t = 10
steps = int(max_t/dt)

ts, xs = simulate(zero_potential(), method=method, num_particles=num_particles, max_t=max_t, dt=dt)
SD = np.zeros(shape=(num_particles, steps-1))
for i in range(num_particles):
    SD[i] = [(xs[t,i] - xs[0,i])**2 for t in range(steps-1)]

# SD[:,t] is an array with all the different SD values
# (from the different particles) in the time step t
MSD = np.zeros(steps-1)
VAR = np.zeros(steps-1)
for t in range(steps-1):
    MSD[t] = np.mean(SD[:,t])
    VAR[t] = np.var(SD[:,t])

linear = Model(linear_func)
data = RealData(ts[:-1], MSD, np.max(VAR))
odr = ODR(data, linear, beta0=[1.3, 0.4])
out = odr.run()
m, b = out.beta[0], out.beta[1]
sm, sb = out.sd_beta[0], out.sd_beta[1]

with open('../data/MSD_example_{}.data'.format(method), 'w') as f:
    f.write('#m={}+/-{}\nb={}+\-{}\n'.format(m, b, sm, sb))
    for i, t in enumerate(ts[:-1]):
        f.write('{} {} {} {} {}\n'.format(t, MSD[i], VAR[i], err_MSD, err_VAR))
