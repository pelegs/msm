#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import numpy as np
import pyemma


# Trajectory
data = np.load('st2d.npy')[:,:,0]

# Clustering
cluster_centers = np.array([[-6, -6],
                    [0, 0],
                    [1, 5],
                    [5, 1]])
cluster_dtrajs = pyemma.coordinates.assign_to_centers(data, cluster_centers)

# ITS
its = pyemma.msm.its(cluster_dtrajs, lags=np.linspace(1, 50000, 20).astype(int), nits=1, errors='bayes')

# Save
its.save('its_full', overwrite=True)
