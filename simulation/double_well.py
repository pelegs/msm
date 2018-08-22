#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

g0 = gaussian(center=-2)
g1 = gaussian(center=+2)
u = potential(gaussians=[g0, g1])
p = particle()

t_max = int(sys.argv[1])
run_simulation(particle=p,
               potential=u,
               t_max=t_max,
               name='double_well')
