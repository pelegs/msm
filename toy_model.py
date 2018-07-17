""" Simple particle in a N-wells
    model for a basic analysis """

import numpy as np
import sys

def force(x):
    """ F = -dU(x)/dx """
    F = -E * np.sum([2*(k+1) * c * x**(2*k+1) * (-1)**(n-k)
                     for k, c in enumerate(constants)])
    return F

#def force(x):
#    return -E * (4*constants[1]*x**3 - 2*x)

constants = [1.0, 0.2, 0.01]
n = len(constants)-1
E = 5.0E+1
D = 5.0E-2
kBT = 1E-0
s_2D = np.sqrt(2*D)
D_kBT = D/kBT

dt = 1E-1
s_2Ddt = np.sqrt(2*D*dt)
x = 0.0 #[0]
v_dt = 0.0 #[0]
num_steps = 10000000

print('#{} steps, E={}, kBT={}, sqrt(2D)={}, D/kBT={}, dt={}'.format(n, E, kBT, s_2D, D_kBT, dt))
for t in range(num_steps):
    sys.stderr.write('step {}/{}            \r'.format(t, num_steps))
    
    #v_dt.append(force(x[-1])*D_kBT*dt**2 + np.random.normal(0, 1)*s_2D)
    #x.append(x[-1] + v_dt[-1])
    v_dt = force(x)*D_kBT*dt**2 + np.random.normal(0, 1)*s_2D
    x += v_dt
    print(t, x, v_dt)
    if (np.isnan(x) or np.isnan(v_dt)):
    	break

#x_bins = 500
#x_interval = np.linspace(min(x), max(x), x_bins)
#min_x = min(x)
#L = max(x) - min(x)
#v_vs_x = [[] for _ in x_interval]
#for pos, vel in zip(x, v_dt):
#    key = int(np.floor((pos-min_x)/L*x_bins))
#    if key < x_bins:
#        v_vs_x[key].append(np.abs(vel))
#
#for i, vels in enumerate(v_vs_x):
#    if len(vels) != 0:
#        print(x_interval[i], np.average(vels), np.std(vels))
