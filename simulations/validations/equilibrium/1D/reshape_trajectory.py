#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

from sys import argv
import numpy as np

# CL arguments
name = argv[1]
minid = int(argv[2])
maxid = int(argv[3])

data = np.load('data/equib_1D_{}_id{}.npy'.format(name, minid))
for id in range(minid+1, maxid+1):
    print(id)
    data = np.append(data, np.load('data/equib_1D_{}_id{}.npy'.format(name, id)), axis=2)
print('Shape:', data.shape)

np.save('data/equib_1D_{}_all.npy'.format(name), data)
