#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import simulate, gaussian, potential
import numpy as np
import pyemma


# CL arguments
m_val = float(sys.argv[1])
num_steps = int(sys.argv[2])
dt = float(sys.argv[3])
num_clusters = int(sys.argv[4])

# Potential parameters
g1 = gaussian(np.ones(1),
              np.array([-m_val]),
              np.array([3]))
g2 = gaussian(np.ones(1),
              np.array([+m_val]),
              np.array([3]))
U = potential([g1, g2])

# Simulation Parameters
parameters = {
    'name': 'kramers_test',
    'num_steps': num_steps,
    'num_dim': 1,
    'num_particles': 1,
    'KBT': 1,
    'Ddt': 0.001,
    'x0': -m_val,
    'potential': U
}

# Simulation
print('Simulating')
xs = simulate(parameters).flatten()

# Clustering
print('Clustering')
cluster = pyemma.coordinates.cluster_kmeans(xs, k=num_clusters, max_iter=50)

# ITS
print('Calculating ITS')
its = pyemma.msm.its(cluster.dtrajs, lags=np.linspace(1, 10000, 10).astype(int), nits=1, errors='bayes')

# MSM
LAG = 5000
print('Calculating MSM')
bayesian_msm = pyemma.msm.bayesian_markov_model(cluster.dtrajs, lag=LAG, conf=0.95)
sample_mean = bayesian_msm.sample_mean('timescales', k=1)
sample_conf_l, sample_conf_r = bayesian_msm.sample_conf('timescales', k=1)

# Save data
with open('data/kr2_{:0.2f}.data'.format(m_val), 'w') as f:
    f.write('{} {} {} {}\n'.format(m_val, sample_mean[0]*dt, sample_conf_l[0]*dt, sample_conf_r[0]*dt))
print('Done.')
