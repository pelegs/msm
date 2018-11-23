#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
from simlib import *


num_particles = 100
method = 'smol'

num_bins = 150
bins = np.linspace(-10, 10, num_bins)

max_t = 10
dt = 0.001
x0 = 0.0
beta = 1.0
D = 1.0

# ============= Single well ============= #

m = 0
s = 1.5
gs = [gaussian(m, s)]
U = gaussian_potential(gs)

ts, xs = simulate(method=method, potential=U,
                  num_particles=num_particles, x0=x0, D=D, beta=beta,
                  dt=dt, max_t=max_t)

hist = np.zeros(shape=(num_particles, num_bins-1))
for i in range(num_particles):
    hist[i], _ = np.histogram(xs[:,i], bins)
mean_hist = np.mean(hist, axis=0)

filename = '../data/gaussian_one_well_{}_num_particles_{}_dt_{}_D_{}_b_{}_x0_{}.data'.format(method,
                                                                                             num_particles,
                                                                                             dt,
                                                                                             D, beta, x0)
with open(filename, 'w') as f:
    for b, h in zip(bins, mean_hist):
        f.write('{} {}\n'.format(b, h))

# ============= Double well ============= #

m = [-3, 3]
s = [1.5, 1.5]
gs = [gaussian(mi, si) for mi, si in zip(m, s)]
U = gaussian_potential(gs)

ts, xs = simulate(method=method, potential=U,
                  num_particles=num_particles, x0=x0, D=D, beta=beta,
                  dt=dt, max_t=max_t)

hist = np.zeros(shape=(num_particles, num_bins-1))
for i in range(num_particles):
    hist[i], _ = np.histogram(xs[:,i], bins)
mean_hist = np.mean(hist, axis=0)

filename = '../data/gaussian_double_well_{}_num_particles_{}_dt_{}_D_{}_b_{}_x0_{}.data'.format(method,
                                                                                                num_particles,
                                                                                                dt,
                                                                                                D, beta, x0)
with open(filename, 'w') as f:
    for b, h in zip(bins, mean_hist):
        f.write('{} {}\n'.format(b, h))

# ============= Triple well ============= #

m = [-4, 0, 4]
s = [1, 2, 1]
gs = [gaussian(mi, si) for mi, si in zip(m, s)]
U = gaussian_potential(gs)

ts, xs = simulate(method=method, potential=U,
                  num_particles=num_particles, x0=x0, D=D, beta=beta,
                  dt=dt, max_t=max_t)

hist = np.zeros(shape=(num_particles, num_bins-1))
for i in range(num_particles):
    hist[i], _ = np.histogram(xs[:,i], bins)
mean_hist = np.mean(hist, axis=0)

filename = '../data/gaussian_triple_well_{}_num_particles_{}_dt_{}_D_{}_b_{}_x0_{}.data'.format(method,
                                                                                                num_particles,
                                                                                                dt,
                                                                                                D, beta, x0)
with open(filename, 'w') as f:
    for b, h in zip(bins, mean_hist):
        f.write('{} {}\n'.format(b, h))

# ============= Multiple well ============= #

m = [7, -14,  -7,  -1, -11,   2,  14]
s = [2, 2, 2, 1, 1, 3, 2]
gs = [gaussian(mi, si) for mi, si in zip(m, s)]
U = gaussian_potential(gs)

ts, xs = simulate(method=method, potential=U,
                  num_particles=num_particles, x0=x0, D=D, beta=beta,
                  dt=dt, max_t=max_t)

hist = np.zeros(shape=(num_particles, num_bins-1))
for i in range(num_particles):
    hist[i], _ = np.histogram(xs[:,i], bins)
mean_hist = np.mean(hist, axis=0)

filename = '../data/gaussian_multiple_well_{}_num_particles_{}_dt_{}_D_{}_b_{}_x0_{}.data'.format(method,
                                                                                                num_particles,
                                                                                                dt,
                                                                                                D, beta, x0)
with open(filename, 'w') as f:
    for b, h in zip(bins, mean_hist):
        f.write('{} {}\n'.format(b, h))
