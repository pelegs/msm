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

dt = 0.1
max_t = 10
steps = int(max_t/dt)

N = 50
Ds = np.linspace(10, 0.5, N)
ms = np.zeros(N)
sd = np.zeros(N)

for d, D in enumerate(Ds):
    ts, xs = simulate(zero_potential(), method=method, num_particles=num_particles, D=D, max_t=max_t, dt=dt)
    # xs[:,i] is the trajectory of particle i
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
    ms[d] = out.beta[0]
    sd[d] = out.sd_beta[0]

data = RealData(Ds, ms, sy=sd)
odr = ODR(data, linear, beta0=[2, 0.0])
out = odr.run()

with open('../data/MSD_validation_{}.data'.format(method), 'w') as f:
    f.write('# m={}±{}, b={}±{}\n'.format(out.beta[0], out.beta[1],
                                          out.sd_beta[0], out.sd_beta[1]))
    for d, m, v in zip(Ds, ms, sd):
        f.write('{} {} {}\n'.format(d, m, v))
