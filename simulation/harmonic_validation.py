#!/usr/bin/env python3

import numpy as np
from scipy.special import erf
from tqdm import tqdm

import sys
sys.path.append('../lib')
from simlib import *


def gen_int(x, m, s):
    return s*erf((x-m)/(np.sqrt(2)*s))/(2*np.abs(s))

def integral(x1, x2, m, v):
    s = np.sqrt(v)
    return gen_int(x2, m, s) - gen_int(x1, m, s)


method = sys.argv[1]

num_particles = 500

max_t = 15
dt = 0.1
ts = np.arange(0, max_t, dt)

num_repetitions = 100
num_steps = int(max_t/dt)
xs = np.zeros(shape=(num_repetitions, num_steps, num_particles))

Ds = [0.5, 1.0, 1.5]
ks = [0.75, 1.0, 1.5]
betas = [0.75, 1.0, 1.5]
x0s = [-3, 2]

params = [(D, k, beta, x0)
           for D in Ds for k in ks for beta in betas for x0 in x0s]

bins = np.arange(-5, 5, 0.1)
num_bins = len(bins)-1

for D, k, beta, x0 in tqdm(params):
    U = harmonic_potential(k=k)
    for i in range(num_repetitions):
        ts, xs[i] = simulate(U, method=method, num_particles=num_particles, max_t=max_t, dt=dt, beta=beta, x0=x0, D=D)

    m = x0 * np.exp(-D*beta*k*ts)
    v = 1/(beta*k)*(1-np.exp(-2*D*beta*k*ts))

    hist = []
    mean_x = []
    var_x = []
    for i in range(num_repetitions):
        hist.append(np.array([np.histogram(x, bins)[0] for x in xs[i][1:]]))
    hist = np.array(hist)
    mean_hist = np.mean(hist, axis=0)

    # the reason for [1:] in the means and stdevs is that at the first time step the distribution is a delta function,
    # and thus it's histogram can't be plotted
    expected = num_particles * np.array([[integral(bins[j], bins[j+1], mean, var) for j, _ in enumerate(bins[:-1])]
                                          for mean, var in zip(m[1:], v[1:])])

    steps = int(max_t/dt)
    mean_x = np.zeros(steps)
    var_x = np.zeros(steps)
    for i in range(steps):
        mean_x[i] = np.mean(xs[:,i].flatten())
        var_x[i] = np.var(xs[:,i].flatten())

    with open('../data/harmonic_validation_{}_D{}_k{}_beta_{}_x0_{}.data'.format(method, D, k, beta, x0), 'w') as f:
        f.write('# Num repetitions: {}; D={}, k={}, beta={}, x0={}\n'.format(num_repetitions, D, k, beta, x0))
        for i, t in enumerate(ts[1:]):
            fit = [1 if (e-np.sqrt(e) <= h <= e+np.sqrt(e)) else 0 for h, e in zip(mean_hist[i], expected[i])]
            p = np.sum(fit)/num_bins*100
            f.write('{} {} {} {}\n'.format(t, mean_x[i], var_x[i], p))
