#!/usr/bin/env python3

import sys
sys.path.append('../../lib')
from simlib import *

# Test
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib import rc
import numpy as np
from scipy.stats import linregress
import pyemma
from tqdm import tqdm


def make_graph(data, cluster, its, m):
    fig, axes = plt.subplots(1, 1, figsize=(12, 3))
    pyemma.plots.plot_implied_timescales(its,
                                         ylog=False,
                                         ax=axes,
                                         outfile='m_{:0.2f}.png'.format(m)
                                         )
    plt.title('m={:0.2f}'.format(m))
    fig.tight_layout()


# Potential
num_sims = 40
ms = np.linspace(0.5, 4.0, num_sims)
Amp = np.ones(shape=(num_sims, 2, 2))
Mu = np.array([np.array([[-m, 0], [m, 0]]) for m in ms])
Sig = np.ones(shape=(num_sims, 2, 2))
Us = [potential(A, M, S) for A, M, S in zip(Amp, Mu, Sig)]
params = []
for m, U in zip(ms, Us):
    params.append({
                    'name': 'libtest1',
                    'num_steps': 1000000,
                    'num_dim': 2,
                    'beta': 1,
                    'Ddt': 0.01,
                    'x0': np.array([m, 0]),
                    'potential': U
                    })

# Simulation
timescales = []
tmax = [100*np.exp((m)**2/2) for i, m in enumerate(ms)]
for i, (p, m) in tqdm(enumerate(zip(params, ms))):
    print('\n\nSimulation {} of {}'.format(i+1, len(ms)))
    trajectory = simulate(p)
    print('\n\n')
    cluster = pyemma.coordinates.cluster_kmeans(trajectory, k=2, max_iter=100)
    lags = np.linspace(1, tmax[i], 20).astype(int)
    its = pyemma.msm.its(cluster.dtrajs, lags=lags, nits=1, errors='bayes')
    print('\n\n')
    timescales.append(its.timescales)
    make_graph(trajectory, cluster, its, m)

# Linear regression
ts = [np.max(t.flatten()) for t in timescales]
dGs = np.array([m**2/2 for m in ms])
M, b, r, _, _ = linregress(dGs, np.log(ts))
theory = dGs * M + b
with open('correlation.data', 'w') as f:
    for dG, it in zip(dGs, ts):
        f.write('{} {}\n'.format(dG, it))

# Linear plot
rc('text', usetex=True)
plt.figure(figsize=(20,10))
plt.plot(dGs, theory)
plt.plot(dGs, np.log(ts), 'o')
plt.xlabel(r'$\Delta G \left(=\frac{\mu^{2}}{2}\right)$')
plt.ylabel(r'$\log \tau$')
plt.title(r'Time scales vs. Barrier height')
plt.savefig('plot.png')
