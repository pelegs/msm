#!/usr/bin/env python3

import numpy as np
import sys

class gaussian:
    def __init__(self, center=0, stdev=1, amplitude=1):
        self.m = center
        self.s = stdev
        self.a = amplitude

    def get_value(self, x):
        return self.a * np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))

class potential:
    def __init__(self, gaussians=[]):
        self.gaussians = gaussians

    def get_value(self, x):
        return -np.log(np.sum([gauss.get_value(x) for gauss in self.gaussians]))

    def get_force(self, x):
        val = np.sum([-g.get_value(x)*(x-g.m)/g.s**2.0 for g in self.gaussians])
        norm = np.sum([g.get_value(x) for g in self.gaussians])
        return val / norm * E

class particle:
    def __init__(self, x0=0):
        self.x = x0

    def move(self, u, dt):
        drift = u.get_force(self.x) * D_KBT
        noise = S2D * np.random.normal(0.0, 1.0)
        v = drift + noise
        self.x = self.x + v*dt

n = np.random.randint(15, 40)
g = [gaussian(center=np.random.uniform(-30,30),
              stdev=np.random.uniform(0.0, 5.0),
              amplitude=np.random.uniform(0.1, 4.0))
     for _ in range(n)]
u = potential(gaussians=g)
p = particle()

E = 0.01
t_max = 10000
dt = 0.01
D = 5.0
KBT = 1.0
D_KBT = D/KBT
S2D = np.sqrt(2*D)

for t in np.arange(0, t_max, dt):
    sys.stderr.write('\rt={:3.4f} (of {:3.4f})   '.format(t, t_max))
    p.move(u, dt)
    print(t, p.x, u.get_value(p.x), 1E4*u.get_force(p.x))
