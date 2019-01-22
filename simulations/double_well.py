#!/usr/bin/env python3

import numpy as np
from scipy.special import erf
import sys
sys.path.append('../lib')
from libsim import simulate, simulate_histogram


def integral(a, b, M, S, N=1):
    return N/(2*len(M)) * np.sum([erf((b-m)/(np.sqrt(2)*s)) - erf((a-m)/(np.sqrt(2)*s))
                                 for m, s in zip(M, S)])


name = 'double_well'
num_particles = 5000
M = np.array([-3, 3]).astype(np.float64)
S = np.array([1, 1]).astype(np.float64)
D = 1
beta = 1
dt = 0.001
total_steps = 50000
equilibration_time = 50
xmin, xmax = [-7, 7]

print('Simulation:', name)
print('Equilibration time = {}%'.format(equilibration_time/total_steps*100))

x0 = 0.0
num_bins = 150
bins = np.linspace(xmin, xmax, num_bins).astype(np.float64)
hist = simulate(name,
                num_particles,
                random=1, xmin=xmin, xmax=xmax,
                S=S, M=M,
                D=D, beta=beta,
                dt=dt, total_steps=total_steps, equilibration_time=equilibration_time,
                )
