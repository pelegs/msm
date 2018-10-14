#!/usr/bin/env python3

import numpy as np

x0 = np.random.uniform(-5.0, 5.0)
D = 0.5
b = 0.1
c = 1.0
dt = np.random.uniform(0.01, 5.0)
s = np.sqrt(2*D*dt)
m = x0-D*b*c*dt
n = 100000

def P(x):
    return 1/np.sqrt(4*np.pi*D*dt) * np.exp(-(x-x0+D*b*c*dt)**2/(4*D*dt))

xs = np.random.normal(m, s, size=(n, 1)).flatten()
x_min = np.min(xs)
x_max = np.max(xs)

print('*** dt =', dt)

with open('smol.data', 'w') as g:
    g.write('\n'.join(map(str, xs)))

with open('p.data', 'w') as f:
    for x in np.arange(x_min, x_max, 0.01):
        f.write('{} {}\n'.format(x, P(x)))
