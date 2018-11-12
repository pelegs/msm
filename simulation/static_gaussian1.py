#!/usr/bin/env python3

import numpy as np
from tqdm import tqdm

import sys
sys.path.append('../lib')
from simlib import *


method = sys.argv[1]

def gauss(x, m, s):
    return 1/np.sqrt(2*np.pi*s**2) * np.exp(-(x-m)**2/(2*s**2))

def expected_p(x):
    return 0.5 * (gauss(x, -3, 1) + gauss(x, 3, 1))


g1 = gaussian(-3)
g2 = gaussian(+3)
U = gaussian_potential([g1, g2])
num_particles = 100
ts, xs = simulate(U, method=method, num_particles=num_particles, max_t=50000, x0=0, D=0.5)

bins = 150
hist = np.zeros(shape=(bins, num_particles))
bin_edges = np.zeros(shape=(bins+1, num_particles))
for i in range(num_particles):
        hist[:,i], bin_edges[:,i] = np.histogram(xs[100:-1,i], bins=bins, density=True)

hist = np.zeros(shape=(bins, num_particles))
bin_edges = np.zeros(shape=(bins+1, num_particles))
for i in range(num_particles):
    hist[:,i], bin_edges[:,i] = np.histogram(xs[100:-1,i], bins=bins, density=True)

avg_hist = np.zeros(bins)
avg_bin_edges = np.zeros(bins)
for i in range(bins):
    avg_hist[i] = np.mean(hist[i,:])
    avg_bin_edges[i] = np.mean(bin_edges[i,:])

with open('../data/static_gaussian1_{}.data'.format(method), 'w') as f:
    for b, h in zip(avg_bin_edges, avg_hist):
        f.write('{} {} {}\n'.format(b, h, expected_p(b)))
