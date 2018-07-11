""" Simple particle in a N-wells
    model for a basic analysis """

import numpy as np
import sys

def force(x):
    """ F = -dU(x)/dx """
    F = -E*np.sum([2*(k+1) * c * x**(2*k+1) * (-1)**(n-k)
                   for k, c in enumerate(constants)])
    return 0.0#F

constants = [.0, 0.1]
n = len(constants)
E = 1.0E-5
D = 1.0E-5
kBT = 1.0E-1
s_2D = np.sqrt(2*D)
D_kBT = D/kBT

dt = 1E-1
s_dt = np.sqrt(dt)
x = [1/np.sqrt(2*constants[1])]
num_steps = 100000

print('{} steps, E={}, kBT={}, sqrt(2D)={}, D/kBT={}, dt={}'.format(n, E, kBT, s_2D, D_kBT, dt))
for t in range(num_steps):
	sys.stderr.write('step {}/{}    \r'.format(t, num_steps))

	x.append(x[-1] + force(x[-1])*D_kBT*dt + np.random.normal(0, s_2D)*s_dt)
	print(t, x[-1])
	if np.isnan(x[-1]):
		break
