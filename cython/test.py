#!/usr/bin/env python3

from libsim import simulate
import numpy as np
from scipy.special import erf

N = 1000
M = np.array([-3,3]).astype(np.float64)
S = np.array([1,1]).astype(np.float64)
D = 1
beta = 1
dt = 0.001
steps = 100000
x0 = 0
x_eq = 100
eq_f = 1-x_eq/steps
print('Eqilibration fraction: {}%'.format((1-eq_f)*100))

x0s = np.ones(N) * x0
xs = simulate(x0s, S=S, M=M, dt=dt, beta=beta, D=D, steps=steps)

num_bins = 250
bins = np.linspace(-10, 10, num_bins)
hist = np.zeros(shape=(N, num_bins-1))
for i in range(N):
    hist[i], _ = np.histogram(xs[x_eq:,i], bins)
mean_hist = np.mean(hist, axis=0)

def integral(a, b, M, S):
    return 1/(2*len(M)) * np.sum([erf((b-m)/(np.sqrt(2)*s)) - erf((a-m)/(np.sqrt(2)*s))
                        for m, s in zip(M, S)])

expected = steps * eq_f * np.array([integral(bins[i], bins[i+1], M, S)
                        for i in range(num_bins-1)])

print(np.sum(mean_hist), np.sum(expected))

with open('test.data', 'w') as f:
    for b, h, e in zip(bins, mean_hist, expected):
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
