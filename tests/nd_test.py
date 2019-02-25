#!/usr/bin/env python3

"""
Guide for slicing:
pos gets a slice of the form [time, particle id, dimension].
Thus the following matrices are:
    * pos[t,:,:]: Positions of all particles in all dimensions for time t
    * pos[:,i,:]: All positions in all dimensions for particle i
    * pos[:,:,d]: Positions of all particles in all time for dimension d
"""

import numpy as np
from numpy import sqrt, exp, pi


sqrt2pi = 1/sqrt(2*pi)

def matrix_range(min, max, shape):
    matrix = np.zeros(shape)
    array = np.linspace(min, max, shape[0]*shape[1])
    for i in range(shape[0]):
        matrix[i] = array[i*shape[1]:i*shape[1]+shape[1]]
    return matrix

def gaussian(x, a, m, s):
    return a * sqrt2pi/s * exp(-(x-m)**2/(2*s**2))

def force(x, a, m, s):
    return (m-x)/s**2

def total_force_dim(x, dim, A, M, S):
    C = np.sum(force(x, A[dim], M[dim], S[dim]))
    #return np.sum(gaussian(x, A[dim], M[dim], S[dim]))

def drift_matrix(pos, a, m, s):
    drift = np.zeros(shape=pos.shape)
    for i, row in enumerate(pos):
        for j, x in enumerate(row):
            drift[i, j] = total_force_dim(x, j, a, m, s)
    return drift

# Simulation parameters
sqrt2pi = 1/sqrt(2*pi)
beta = 1
dt = 0.01
D = 1
A = D * beta * dt
B = sqrt(2*D*dt)

num_particles = 3
num_dim = 2
time_steps = 10000
num_gaussians = 5
min_pos, max_pos = (0, 0)

# Gaussian matrices
Amp   = np.ones(shape=(num_dim, num_gaussians))
Mu    = np.zeros(shape=(num_dim, num_gaussians))
Sigma = np.ones(shape=(num_dim, num_gaussians))

# Define general position array
pos = np.zeros(shape=(time_steps, num_particles, num_dim))

# Set initial position at random in all axis for all particles
pos[0] = np.random.uniform(min_pos, max_pos, size=(num_particles, num_dim))

# Motion
for t in range(1, time_steps):
    noise = np.random.normal(0, 1, size=(num_particles, num_dim))
    pos[t] = pos[t-1] + B*noise

# Print
for t, row in enumerate(pos):
    print(t, ' '.join(map(str, row.flatten())))

"""
# Create a mean-square displacement matrix
def MSD_matrix(pos):
    matrix = np.zeros(shape=(time_steps-1, num_dim))

    # Create separate MSD per dimension
    for dim, _ in enumerate(pos[0,0,:]):
        i_pos = pos[:,:,dim] # see guide
        i_pos_diff_sqr = np.zeros(shape=(time_steps-1, num_particles))
        i_pos_diff_sqr[0] = np.zeros(num_particles)
        for t in range(1, time_steps-1):
            i_pos_diff_sqr[t] = i_pos_diff_sqr[t-1] + (i_pos[t,:] - i_pos[t-1,:])**2
        # Calculate mean all aprticles per each time step
        matrix[:,dim] = np.mean(i_pos_diff_sqr, axis=1)

    return matrix

MSD = MSD_matrix(pos)
for t, row in enumerate(MSD):
    print(t, ' '.join(map(str, row)))
"""
