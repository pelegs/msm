#!/usr/bin/env python3

from libsim import simulate_hist
import numpy as np
from scipy.special import erf

N = 1000
M = np.array([-2.5,2.5]).astype(np.float64)
S = np.array([1,1]).astype(np.float64)
D = 5
beta = 1
dt = 0.001
total_steps = 500000
step_block = 1000
x0 = 0
x_eq = 100
eq_f = 1-x_eq/total_steps
print('Eqilibration fraction: {:0.2f}%'.format((1-eq_f)*100))

num_bins = 100
bins = np.linspace(-10, 10, num_bins).astype(np.float64)
x0s = (np.ones(N) * x0).astype(np.float64)
hist = simulate_hist(x0s, bins,
                     S=S, M=M, beta=beta, D=D,
                     dt=dt, total_steps=total_steps,
                     step_block=step_block, eq_time=x_eq,) * total_steps

def integral(a, b, M, S):
    return 1/(2*len(M)) * np.sum([erf((b-m)/(np.sqrt(2)*s)) - erf((a-m)/(np.sqrt(2)*s))
                        for m, s in zip(M, S)])

exp_norm_factor = total_steps//(total_steps//step_block) * eq_f
expected = total_steps * np.array([integral(bins[i], bins[i+1], M, S)
                                  for i in range(num_bins-1)])

print(np.sum(hist), np.sum(expected))

with open('test.data', 'w') as f:
    for b, h, e in zip(bins, hist, expected):
        f.write('{} {} {}\n'.format(b, h, e))

"""
SD = np.zeros(shape=(N, steps))
for i in range(N):
    SD[i] = [(xs[t,i]-xs[0,i])**2 for t in range(steps)]
MSD = np.mean(SD, axis=0)
with open('test.data', 'w') as f:
    for t, m in enumerate(MSD):
        f.write('{} {}\n'.format(t, m))
"""
