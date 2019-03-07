#!/usr/bin/env python3

import numpy as np
from numpy import exp, sqrt, pi, log
sqrt_2pi = 1/sqrt(2*pi)
from tqdm import tqdm


def gauss(x, a, m, s):
    return a * sqrt_2pi/s * exp(-(x-m)**2/(2*s**2))

def gauss_axis(x, A, M, S):
    return np.sum([gauss(x, a, m, s) for a, m, s in zip(A, M, S)])

def potential(X, A, M, S, beta=1):
    return -beta*log(np.prod([gauss_axis(x, A[dim], M[dim], S[dim])
                              for dim, x in enumerate(X)]))

def force(X, A, M, S, beta=1):
    pass


"""
Example for parameters:
Amp = np.array([[1, 1],
                [1, 1, 1],
                [1, 1]])
Mu  = np.array([[-5, 5],
                [-3, 0, 3],
                [-4, 4]])
Sig = np.array([[1, 1],
                [1, 1, 1],
                [1, 1]])
"""

num_particles = 500
num_dim = 1
num_steps = 100
num_gaussians = 2

dt = 0.01
beta = 1
D = 1
A = D*beta*dt
B = np.sqrt(2*D*dt)

Xs = np.zeros(shape=(num_steps, num_particles, num_dim))

for t in tqdm(range(1, num_steps)):
    for p in range(num_particles):
        drift = 0 #A*potential(Xs[t-1,p,:], Amp, Mu, Sig)
        noise = B*np.random.normal(size=num_dim)
        Xs[t,p,:] = Xs[t-1,p,:] + drift + noise

mean = np.mean(Xs[:,:,0], axis=1)
var = np.var(Xs[:,:,0], axis=1)

for t, m, v in zip(range(num_steps), mean, var):
    print(t, m, v)