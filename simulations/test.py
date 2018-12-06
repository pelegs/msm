#!/usr/bin/env python3


import numpy as np
from scipy.special import erf
import sys
sys.path.append('../lib')
print(sys.path)
from libsim import simulate_hist

name = 'double_well'
num_particles = 1000
M = np.array([-3,3]).astype(np.float64)
S = np.array([1,1]).astype(np.float64)
D = 50
beta = 0.1
dt = 0.001
total_steps = 500000
step_block = 5000
x0 = 0.0
x_eq = 1000
eq_f = 1-x_eq/total_steps

print('Simulation:', name)
print('Eqilibration fraction: {:0.2f}%'.format((1-eq_f)*100))

num_bins = 150
bins = np.linspace(-9, 9, num_bins).astype(np.float64)
x0s = np.random.uniform(-9, 9, num_particles).astype(np.float64)
hist, error = simulate_hist(x0s, bins,
                            S=S, M=M, beta=beta, D=D,
                            dt=dt, total_steps=total_steps,
                            step_block=step_block, eq_time=x_eq,)

def integral(a, b, M, S):
    return 1/(2*len(M)) * np.sum([erf((b-m)/(np.sqrt(2)*s)) - erf((a-m)/(np.sqrt(2)*s))
                        for m, s in zip(M, S)])

exp_norm_factor = total_steps * eq_f
expected = exp_norm_factor * np.array([integral(bins[i], bins[i+1], M, S)
                            for i in range(num_bins-1)])

with open('../data/{}.data'.format(name), 'w') as f:
    for b, h, err, exp in zip(bins, hist, error, expected):
        f.write('{} {} {} {}\n'.format(b, h, err, exp))
