""" Simple brownian particle """

import numpy as np
import sys

D = 1.337E+1
kBT = 1E+1
dt = 1E0
s_2Ddt = np.sqrt(2*D*dt)
x = [0.0]
num_steps = 1000000

print('#{} steps, kBT={}, sqrt(2Ddt)={}, dt={}'.format(num_steps, kBT, s_2Ddt, dt))
for t in range(num_steps):
	sys.stderr.write('step {}/{}            \r'.format(t, num_steps))
	v_dt = np.random.normal(0, 1)*s_2Ddt
	x.append(x[-1] + v_dt)
	print(t, x[-1], v_dt)
	if np.isnan(x[-1]):
		break
