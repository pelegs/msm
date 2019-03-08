#!/usr/bin/env python3

import numpy as np
from numpy import exp, sqrt, pi, log
sqrt_2pi = 1/sqrt(2*pi)
from tqdm import tqdm
from scipy.stats import linregress
from sys import stderr


def gauss(x, a, m, s):
    return a * sqrt_2pi/s * exp(-(x-m)**2/(2*s**2))

def gauss_force_dim(x, A, M, S, beta=1.0):
    dg = np.sum([(m-x)/s**2*gauss(x, a, m, s) for a, m, s in zip(A, M, S)])
    g  = np.sum([gauss(x, a, m, s) for a, m, s in zip(A, M, S)])
    if g == 0:
        return 0
    else:
        return beta * dg/g

def force(X, A, M, S, beta=1.0):
    return np.array([gauss_force_dim(x, a, m, s)
                     for x, a, m, s in zip(X, A, M, S)])

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

num_particles = 100
num_dim = 1
num_steps = 5000
num_gaussians = 2

dt = 0.01
beta = 1.0
D = 5.0
A = D*beta*dt
B = np.sqrt(2*D*dt)

Amp = np.ones(shape=(num_dim, num_gaussians))
Mu = np.zeros(shape=(num_dim, num_gaussians))
Mu[:,0] = -3
Mu[:,1] = 3
Sig = np.ones(shape=(num_dim, num_gaussians))

Xs = np.zeros(shape=(num_steps, num_particles, num_dim))
Xs[0,0,:] = np.ones(num_dim) * 3.7

for t in tqdm(range(1, num_steps)):
    for p in range(num_particles):
        drift = A*force(Xs[t-1,p,:], Amp, Mu, Sig, beta)
        noise = B*np.random.normal(size=num_dim)
        Xs[t,p,:] = Xs[t-1,p,:] + drift + noise

        ## Check Force vs. Position
        #forces = force(Xs[t-1,p,:], Amp, Mu, Sig, beta)
        #for x, F in zip(Xs[t-1,p,:], forces):
        #    print(x, F, end=' ')
        #print('')


"""
Sanity checks
"""

def linear_regression():
    # Linear regression (e.g. for MSD check)
    ts = range(num_steps)
    pos = Xs[:,0,:]
    mean = np.mean(pos, axis=1)
    var = np.var(pos, axis=1)
    slope, intercept, r_value, p_value, std_err = linregress(ts, var)
    print('var: y={:0.3f} (2Ddt={:0.3f}) + {:0.3f}, r^2={:0.3f}'.format(slope, 2*D*dt, intercept, r_value))

def mean_var():
    # Mean and Variance check (e.g. for Ornstein-Uhlenbeck process)
    stderr.write('beta = {}, 1/beta = {}, D = {}, 1/D = {}, beta*D = {}, 1/(beta*D)={}\n'.format(beta, 1/beta, D, 1/D, beta*D, 1/(beta*D)))
    mean = np.mean(Xs[:,0,:], axis=1)
    var = np.var(Xs[:,0,:], axis=1)
    for t, m, v in zip(range(num_steps), mean, var):
        print(t, m, v)

def histogram():
    pass
