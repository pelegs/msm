#!/usr/bin/env python3

import numpy as np
from scipy.special import erf
import sys
sys.path.append('../lib')
from libsim import simulate_histogram


def integral(a, b, M, S, N=1):
    return N/(2*len(M)) * np.sum([erf((b-m)/(np.sqrt(2)*s)) - erf((a-m)/(np.sqrt(2)*s))
                                 for m, s in zip(M, S)])


name = 'single_well'
num_particles = 5000
M = np.array([0]).astype(np.float64)
S = np.array([1]).astype(np.float64)
D = 1
beta = 1
dt = 0.001
total_steps = 100000
equilibration_time = 1000

print('Simulation:', name)
print('Equilibration time = {}%'.format(equilibration_time/total_steps*100))

x0 = 0.0
num_bins = 150
bins = np.linspace(-5, 5, num_bins).astype(np.float64)
hist = simulate_histogram(num_particles, x0, bins,
                S=S, M=M,
                D=D, beta=beta,
                dt=dt, total_steps=total_steps, equilibration_time=equilibration_time,
                )

mean_hist = np.mean(hist, axis=0)
stderr_hist = np.std(hist, axis=0)

expected = [integral(bins[i], bins[i+1], M, S, total_steps) for i in range(num_bins-1)]

with open('../data/{}.data'.format(name), 'w') as f:
    for x, m, err, exp in zip(bins[:-1], mean_hist, stderr_hist, expected):
        f.write('{} {} {} {}\n'.format(x, m, err, exp))
