#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import sys
sys.path.append('/home/psapir/prog/msm/lib')
from simlib import *
import numpy as np


id = int(sys.argv[1])
num_steps = int(sys.argv[2])
t0 = int(sys.argv[3])
num_particles = int(sys.argv[4])

U = potential()
U.load('potentials/random.pt')

parameters = {
    'name': '2D_equibilibrium',
    'num_steps': num_steps,
    'num_dim': 2,
    'num_particles': num_particles,
    'KBT': 1,
    'Ddt': 0.01,
    'x0': np.random.uniform(-9, 9, size=(2, num_particles)),
    'potential': U
}

xs = simulate(parameters)[t0:,:,:]

np.save('data/2d_rand{}'.format(id), xs)
