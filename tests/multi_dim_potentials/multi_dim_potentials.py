#!/usr/bin/env python3

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

import numpy as np
from numpy import exp, sqrt, pi, log
from scipy.special import erf
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


sqrt_2pi = 1/sqrt(2*pi)
sqrt2 = sqrt(2)

num_particles = 1
num_dim = 2
num_steps = 10000
num_gaussians = 2

dt = 0.01
beta = 1.0
D = 1
A = D*beta*dt
B = np.sqrt(2*D*dt)

Amp = np.ones(shape=(num_dim, num_gaussians))
Mu = np.zeros(shape=(num_dim, num_gaussians))
Sig = np.ones(shape=(num_dim, num_gaussians))
Xs = np.random.uniform(-10, 10, size=(num_steps, num_particles, num_dim))


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

def single_indefinite_integral(x, m, s):
    return erf((m-x)/(sqrt2*s)) / 2

def single_integral(a, b, m, s):
    return single_indefinite_integral(b, m, s) - single_indefinite_integral(a, m, s)

def integral(a, b, M, S, N=1):
    return np.sum([single_integral(a, b, m, s) for m, s in zip(M, S)]) * N / len(M)

def histogram(xmin=-5, xmax=5, dx=0.1, t0=0):
    # Histogram of positions
    pos = Xs[t0:,:,:].flatten()
    frac = 1-(t0/len(Xs))
    bins = np.arange(xmin, xmax, dx)
    hist, _ = np.histogram(pos, bins)
    N = num_steps * num_dim * num_particles * frac
    expectation = [integral(bins[i+1], bins[i], [-3, 3], [1, 1], N) for i, b in enumerate(bins[:-1])]
    for b, h, e in zip(bins, hist, expectation):
        print(b, h, e)

def two_dim_potential():
    Amp = np.array([[1, 1, 1],
                    [1, 0, 1]])
    Mu = np.array([[-6, 0, 6],
                   [-7, 0, 7]])
    Sig = np.array([[1, 1, 1],
                    [1, 1, 1]])
    return Amp, Mu, Sig

def histogram_2d(data, xrange=(-10, 10), yrange=(-10, 10), dx=0.5, dy=0.5):
    xbins = np.arange(xrange[0], xrange[1], dx)
    ybins = np.arange(yrange[0], yrange[1], dy)
    hist, xedges, yedges = np.histogram2d(data[:,0], data[:,1], bins=(xbins, ybins))
    for row in hist:
        print(' '.join(map(str, row)))

def single_trajectory():
    for t, x in enumerate(Xs[:,0,:]):
        print(t, ' '.join(map(str, x)))


"""
SIMULATION
"""
def main_sim():
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


Amp, Mu, Sig = two_dim_potential()
main_sim()
single_trajectory()

#pos = Xs[:,0,:]
#for i in range(1, num_particles):
#    pos = np.concatenate((pos, Xs[:,i,:]), axis=0)
#histogram_2d(pos)
