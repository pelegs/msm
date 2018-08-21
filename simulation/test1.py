#!/usr/bin/env python3

import numpy as np
import sys
sys.path.append('../lib')
sys.path.append('lib')
from simlib import *

n = np.random.randint(4, 10)
g = [gaussian(center=np.random.uniform(-10,10),
              stdev=np.random.uniform(0.0, 2.0),
              amplitude=np.random.uniform(0.1, 2.0))
     for _ in range(n)]
u = potential(gaussians=g)
p = particle()

t_max = int(sys.argv[1])
for t in np.arange(0, t_max, dt):
    sys.stderr.write('\rt={:3.4f} (of {:3.4f})   '.format(t, t_max))
    p.move(u, dt)
    print(t, p.x, u.get_value(p.x), 1E4*u.get_force(p.x))
