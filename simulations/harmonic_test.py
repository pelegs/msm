#!/usr/bin/env python3

import numpy as np
from scipy.special import erf
import sys
sys.path.append('../lib')
from libsim import simulate, simulate_histogram


def integral(a, b, M, S, N=1):
    return N/(2*len(M)) * np.sum([erf((b-m)/(np.sqrt(2)*s)) - erf((a-m)/(np.sqrt(2)*s))
                                 for m, s in zip(M, S)])


name = 'harmonic_test'
num_particles = 1000
M = np.array([0]).astype(np.float64)
S = np.array([1]).astype(np.float64)
D = 1
beta = 1
dt = 0.001
total_steps = 1000
equilibration_time = 50
x0 = 1
x0s = np.ones(num_particles) * x0

print('Simulation:', name)
print('Equilibration time = {}%'.format(equilibration_time/total_steps*100))

hist = simulate(name,
                num_particles,
                random=0, x0s=x0s,
                S=S, M=M,
                D=D, beta=beta,
                dt=dt, total_steps=total_steps, equilibration_time=equilibration_time,
                )
