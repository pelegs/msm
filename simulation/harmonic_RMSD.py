#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
from simlib import *


def th_mean(t, x0=0, D=1, k=1, beta=1):
    return x0 * np.exp(-D*k*beta*t)

def th_var(t, D=1, k=1, beta=1):
    return 1/np.sqrt(k*beta) * (1-np.exp(-2*D*k*beta*t))


method = 'lang'
num_particles = 1000
max_t = 10
dt = 0.01
x0 = 2
D = 1
beta = 1
k = 1
num_steps = int(max_t/dt)

Ns = [100, 300, 500, 1000, 2000, 5000, 10000, 20000, 50000]
DTs = [0.5, 0.2, 0.1, 0.05, 0.01]

RMSD_mean = np.zeros(shape=(len(Ns), len(DTs)))
RMSD_var  = np.zeros(shape=(len(Ns), len(DTs)))

for i, N in enumerate(Ns):
    for j, dt in enumerate(DTs):
        print(N, dt)

        ts, xs = simulate(harmonic_potential(k=k), method=method,
                          num_particles=N, dt=dt, max_t=max_t,
                          x0=x0, D=D, beta=beta)

        mean_predict = th_mean(ts, x0)
        mean_sim = np.mean(xs, axis=1)
        RMSD_mean[i][j] = np.sqrt(np.mean((mean_sim-mean_predict)**2))

        var_predict = th_var(ts)
        var_sim = np.var(xs, axis=1)
        RMSD_var[i][j] = np.sqrt(np.mean((var_sim-var_predict)**2))

with open('../data/harmonic_RMSD_mean.data', 'w') as f:
    for i, row in enumerate(RMSD_mean.T):
        f.write(' '.join(map(str, row)) + '\n')

with open('../data/harmonic_RMSD_var.data', 'w') as f:
    for i, row in enumerate(RMSD_var.T):
        f.write(' '.join(map(str, row)) + '\n')
