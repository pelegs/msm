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


num_particles = 1000
num_dim = 10
time_steps = 100
min_pos, max_pos = (-10, 10)

# Define general position array
pos = np.zeros(shape=(time_steps, num_particles, num_dim))

# Set initial position at random in all axis for all particles
pos[0] = np.random.uniform(min_pos, max_pos, size=(num_particles, num_dim))

# Motion with noise only
for t in range(1, time_steps):
    pos[t] = pos[0] + np.random.normal(0, 1, size=(num_particles, num_dim))

# Create a mean-square displacement matrix
def MSD_matrix(pos):
    matrix = np.zeros(shape=(time_steps-1, num_dim))

    # Create separate MSD per dimension
    for dim, _ in enumerate(pos[0,0,:]):
        i_pos = pos[:,:,dim] # see guide
        i_pos_diff_sqr = np.zeros(shape=(time_steps-1, num_particles))
        for t in range(time_steps-1):
            if t > 0:
                # avoid t=0, hence di is the difference to the last row (array element -1)
                di = i_pos_diff_sqr[t-1]
            else:
                di = np.zeros(num_particles)
            i_pos_diff_sqr[t] = di + (i_pos[t+1,:] - i_pos[t,:])**2 # add displacements
        # Calculate mean all aprticles per each time step
        matrix[:,dim] = np.mean(i_pos_diff_sqr, axis=1)
    return matrix

MSD = MSD_matrix(pos)
for t in range(time_steps-1):
    print(t, ' '.join(map(str, MSD[t,:])))
