""" Simple particle in a N-wells
    model for a basic analysis """

import numpy as np

def force(x):
    """ F = -dU(x)/dx """
    F = -np.sum([(-1)**k * c/(2*k) * x**(2*k-1)
                 for k, c in enumerate(constants)])
    return F

def v(x):
    return force(x) + np.random.normal(0, s2D)

constants = [.0, .5, .01] 
E = 5
D = 1.0
kBT = 100
s2D = np.sqrt(2*D)
D_kBT = D/kBT

dt = 0.01
x = [-1]
num_steps = 1000000

for t in range(num_steps):
    x.append(x[-1] + v(x[-1])*dt)
    print(t, x[-1])
