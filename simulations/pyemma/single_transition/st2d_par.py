#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
from subprocess import call
import numpy as np
import pyemma


id = int(sys.argv[1])
s = int(sys.argv[2])
e = int(sys.argv[3])
max_lag = int(sys.argv[4])
LAG = int(sys.argv[5])
num_lags = int(sys.argv[6])

# Trajectory
start, end = s+id, e+id
data = np.load('trajectories/single_trajectory_full.npy')[start:end,:]

# Clustering
cluster_centers = np.array(
                   [[-6, -6],
                    [0, 0],
                    [1, 5],
                    [5, 1]])
cluster_dtrajs = pyemma.coordinates.assign_to_centers(data, cluster_centers)

# ITS
its = pyemma.msm.its(cluster_dtrajs, lags=np.linspace(1, max_lag, num_lags).astype(int), nits=1, errors='bayes')

#LAG = 25000
bayesian_msm = pyemma.msm.bayesian_markov_model(cluster_dtrajs, lag=LAG, conf=0.95)
sample_mean = bayesian_msm.sample_mean('timescales', k=1)
sample_conf_l, sample_conf_r = bayesian_msm.sample_conf('timescales', k=1)
# Save
rng = '{:06d}_{:06d}'.format(s, e)
call(['mkdir', '-p', 'data/{}'.format(rng)])
with open('data/{}/its_part_{:03d}.data'.format(rng, id), 'w') as f:
    f.write('{} {} {}\n'.format(sample_mean[0], sample_conf_l[0], sample_conf_r[0]))
its.save('data/{}/its_part_{:03d}.pyemma'.format(rng, id), overwrite=True)
