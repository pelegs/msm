#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pyemma


fig, axes = plt.subplots(10, 1, figsize=(12, 20))
fig.tight_layout()

mus = np.arange(3.00, 3.5, 0.05)
print('mu = ({})'.format(', '.join(map(str, mus))))
for i, mu in enumerate(mus):
	text = 'mu={:0.2f}'.format(mu)
	print('Now calculating', text)
	datafile = '../data/dx_{:0.2f}.npy'.format(mu)
	data = np.load(datafile)
	cluster = pyemma.coordinates.cluster_kmeans(data, k=2, max_iter=50)
	lags = np.array([100, 1000, 2000, 5000, 7000], dtype=int)
	its = pyemma.msm.its(cluster.dtrajs, lags=lags, nits=1, errors='bayes')
	plt.title(text)
	pyemma.plots.plot_implied_timescales(its, ylog=False, ax=axes[i], outfile='test.png')
