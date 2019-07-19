#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
import numpy as np
from sympy import *
import pyemma


# From CL
m_val = float(sys.argv[1])
tmax = float(sys.argv[2])

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

# Other Parameters
dt = 0.01

# Forces
F1 = simplify(-diff(U, x))*Ddt/KT
F2 = sqrt(2*Ddt)*R
F = F1 + F2

# Substitute Actuall Values into F
F_val = F.subs(m, m_val).subs(s, 1).subs(KT, 1).subs(Ddt, 0.01)

# Time array
ts = np.arange(0, tmax, dt)

# Positions array
xs = np.zeros(ts.shape[0])

# Randomness array
rs = np.random.normal(0, 1, size=ts.shape[0])

# Simulation
for i, t in enumerate(ts):
    xs[i] = xs[i-1] + F_val.subs(x, xs[i-1]).subs(R, rs[i]).evalf()

# Calculate TS
cluster_centers = np.array([[-m_val],[m_val]])
cluster_dtrajs = pyemma.coordinates.assign_to_centers(xs, cluster_centers)
its = pyemma.msm.its(cluster_dtrajs, lags=np.linspace(1, 5000, 20).astype(int), nits=1, errors='bayes')
LAG = 600
bayesian_msm = pyemma.msm.bayesian_markov_model(cluster_dtrajs, lag=LAG, conf=0.95)
sample_mean = bayesian_msm.sample_mean('timescales', k=1)
sample_conf_l, sample_conf_r = bayesian_msm.sample_conf('timescales', k=1)

# Record data
with open('data/kr_{:0.2f}.data'.format(m_val), 'w') as f:
    f.write('{} {} {} {}'.format(m_val, sample_mean[0], sample_conf_l[0], sample_conf_r[0]))
