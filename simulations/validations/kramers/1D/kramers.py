#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
import numpy as np
from sympy import *
from tqdm import tqdm_notebook
import pyemma


# CL arguments
m_val = float(sys.argv[1])
maxt = float(sys.argv[2])
dt = float(sys.argv[3])
num_clusters = int(sys.argv[4])

# Symbols
x = symbols('x')
m = symbols('mu')
s = symbols('sigma')

# Potential
U = -log(exp(-(x-m)**2/(2*s**2)) + exp(-(x+m)**2/(2*s**2)))

# Brownian Dynamics Parameters
KT = symbols('k_{B}T')
Ddt = symbols('Ddt')
R = symbols('R')

# Forces
F1 = simplify(-diff(U, x))*Ddt/KT
F2 = sqrt(2*Ddt)*R
F = F1 + F2

# Substitute Actuall Values into F
F_val = F.subs(m, m_val).subs(s, 1).subs(KT, 1).subs(Ddt, dt)

# Time array
ts = np.arange(0, maxt, dt)

# Positions array
xs = np.zeros(ts.shape[0])

# Randomness array
rs = np.random.normal(0, 1, size=ts.shape[0])

# Simulation
print('Simulating')
for i, t in enumerate(tqdm_notebook(ts)):
    xs[i] = xs[i-1] + F_val.subs(x, xs[i-1]).subs(R, rs[i]).evalf()

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
with open('data/kr_{:0.2f}.data'.format(m_val), 'w') as f:
    f.write('{} {} {} {}\n'.format(m_val, sample_mean[0]*dt, sample_conf_l[0]*dt, sample_conf_r[0]*dt))
print('Done.')
