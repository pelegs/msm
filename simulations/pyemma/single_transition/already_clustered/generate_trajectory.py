#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import numpy as np
import sys
from tqdm import tqdm

# States
states = np.arange(0, 2, 1).astype(int)
p12 = float(sys.argv[2])
p21 = float(sys.argv[3])
p11 = 1-p12
p22 = 1-p21
T_matrix = np.array([[p11, p12],
                     [p21, p22]])
eig_vals = np.linalg.eigvals(T_matrix)
print(eig_vals)
k_expected = np.sort(eig_vals)[0]
its_expected = -1.0/np.log(np.abs(k_expected))
print(k_expected, its_expected)

# Generate trajectory
num_steps = int(sys.argv[1])
trajectory = np.zeros(num_steps).astype(int)
trajectory[0] = 0
for i, s in enumerate(tqdm(trajectory[:-1])):
    trajectory[i+1] = np.random.choice(states, p=T_matrix[s])

# Save trajectory
np.save('data/full_trajectory', trajectory)
