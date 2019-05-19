#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

from pathlib import Path
home = str(Path.home())
import sys
sys.path.append('{}/prog/msm/lib'.format(home))
import numpy as np
from simlib import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.set_cmap('rainbow')
import pyemma


def simulate(ms, num_trans=2000):
    for i, m in enumerate(ms):
        # Potential
        gaussians = []
        gaussians.append(gaussian(A=np.ones(1),
                                  M=np.array([-m]),
                                  S=np.ones(1)))
        gaussians.append(gaussian(A=np.ones(1),
                                  M=np.array([m]),
                                  S=np.ones(1)))
        U = potential(gaussians)

        # Parameters
        parameters = {
            'name': 'equilibrium_test',
            'num_steps': 1000000,
            'num_dim': 1,
            'num_particles': 1,
            'KBT': 1,
            'Ddt': 0.01,
            'x0': 0.0,
            'potential': U
        }

        # Simulation
        print('### m={:0.2f}'.format(m))
        Xs = simulate_transitions(parameters, num_trans=num_trans)
        np.save('m_{:0.2f}.npy'.format(m), Xs)


def analyze(ms):
    timescales = []
    errors = []
    for i, m in enumerate(ms):
        print('\n\n### m={:0.2f}'.format(m))
        Xs = np.load('m_{:0.2f}.npy'.format(m))
        cluster = pyemma.coordinates.cluster_kmeans(Xs, k=2, max_iter=50)
        lags = np.linspace(1, 1500, 10).astype(int)
        its = pyemma.msm.its(cluster.dtrajs, lags=lags, nits=1, errors='bayes')
        relevant_its = [timescale for timescale, lag in zip(its.timescales[1:], lags)
                        if timescale >= lag]
        #fig, axes = plt.subplots(1, 1, figsize=(10, 5))
        #axes.set_title('m={:0.2f}'.format(m))
        #pyemma.plots.plot_implied_timescales(its, ylog=False, ax=axes,
        #                                     outfile='m_{:0.2f}.png'.format(m))
        #fig.tight_layout()
        timescales.append(np.mean(relevant_its))
        errors.append(np.std(relevant_its))
    with open('timescales.data', 'a') as f:
        for m, time, error in zip(ms, timescales, errors):
            f.write('{:0.2f} {:0.2f} {:0.2f}\n'.format(m, time, error))


if __name__ == '__main__':
    ms = np.arange(0.5, 1.7, 0.01)
    simulate(ms, num_trans=2000)
    analyze(ms)
