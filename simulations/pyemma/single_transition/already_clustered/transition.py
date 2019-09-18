#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import numpy as np
import pyemma
import sys


# Steps
num_steps = int(sys.argv[1])

# Load full trajectory and cut it according to num_steps
trajectory = np.load('data/full_trajectory.npy')[:num_steps]

# Calculate analytical results
trans12_indeces = np.array([i for i, e in enumerate(trajectory[:-1]) if trajectory[i]==0 and trajectory[i+1]==1])
trans21_indeces = np.array([i for i, e in enumerate(trajectory[:-1]) if trajectory[i]==1 and trajectory[i+1]==0])
trans21_indeces = np.insert(trans21_indeces, 0, 0)

if trans12_indeces.shape[0] < trans21_indeces.shape[0]:
    trans12_indeces = np.append(trans12_indeces, 0)

trans12 = trans12_indeces - trans21_indeces
trans12 = trans12[trans12 >= 0]
trans21 = (trans21_indeces - np.insert(trans12_indeces, 0, 0)[:-1])[1:]
trans21 = trans21[trans21 >= 0]

t12 = np.mean(trans12)
t21 = np.mean(trans21)

k12 = 1/t12
k21 = 1/t21
k_mat = np.array([[1-k12, k12],
                  [k21, 1-k21]])
eig_k = np.linalg.eigvals(k_mat)
k_theory = np.sort(eig_k)[0]
its_theory = -1/np.log(np.abs(k_theory))
theory_low, theory_high = k_theory, k_theory

# PyEmma results
its_sim = pyemma.msm.its(trajectory, lags=np.linspace(1, 25, 25).astype(int), nits=1, errors='bayes')
LAG = 15
bayesian_msm = pyemma.msm.bayesian_markov_model(trajectory, lag=LAG, conf=0.95)
sample_mean = bayesian_msm.sample_mean('timescales', k=1)
sample_conf_l, sample_conf_r = bayesian_msm.sample_conf('timescales', k=1)
msm = pyemma.msm.estimate_markov_model(trajectory, lag=LAG)

# Histogram
msm = pyemma.msm.bayesian_markov_model(trajectory, 1, reversible=False,
                                       nsamples=10000, conf=0.95, count_mode='effective',
                                       mincount_connectivity=0, show_progress=True)
xmin, xmax = -3, -1.5
bins = np.logspace(xmin, xmax, 150)
sample_rates = np.array(msm.sample_f('P'))[:,0,1]
sample_rates_hist, bin_edges = np.histogram(sample_rates, bins=bins, normed=False)

# Save data
with open('data/transition_{}.data'.format(num_steps), 'w') as f:
	f.write('{} {} {} {} {} {} {}\n'.format(num_steps,
											its_theory, theory_low, theory_high,
											sample_mean[0], sample_conf_l[0], sample_conf_r[0]))

with open('data/transition_{}.histogram'.format(num_steps), 'w') as g:
	for b, h in zip(bin_edges, sample_rates_hist):
		g.write('{} {}\n'.format(b, h))
