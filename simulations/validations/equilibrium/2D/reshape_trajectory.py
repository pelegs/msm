#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

from sys import argv
import numpy as np

# CL arguments
name = argv[1]
minid = int(argv[2])
maxid = int(argv[3])

# String
base_str = 'data/equib_2D_'

# Read data
data = np.load(base_str + '{}_id{}.npy'.format(name, minid))
for id in range(minid+1, maxid+1):
    print(id, end=' ')
    data = np.append(data, np.load(base_str + '{}_id{}.npy'.format(name, id)), axis=2)
print('\nShape = {}'.format(data.shape))

# Save data
np.save(base_str + '{}_all.npy'.format(name), data)
