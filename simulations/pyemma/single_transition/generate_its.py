#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import pyemma
import numpy as np


# Load data
data = np.load('trajectories/single_trajectory_full.npy')[:,:]

# Create clusters
cluster_centers = np.array([[-6, -6],
                    [0, 0],
                    [1, 5],
                    [5, 1]])
cluster_dtrajs = pyemma.coordinates.assign_to_centers(data, cluster_centers)

# Create ITS
its = pyemma.msm.its(cluster_dtrajs, lags=np.linspace(1, 70000, 20).astype(int), nits=1, errors='bayes')

# Save ITS
its.save('its_full.pyemma', overwrite=True)
