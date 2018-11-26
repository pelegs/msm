from libsim import move
import numpy as np
from scipy.special import erf

N = 5000
m = 0
s = 1
D = 1
beta = 1
dt = 0.001
steps = 100000
x0 = 0.1
x_eq = 1000
eq_f = 1-x_eq/steps
print('eqilibration fraction: {}%'.format((1-eq_f)*100))

x0s = np.ones(N) * x0
xs = move(x0s, s=s, m=m, dt=dt, beta=beta, D=D, steps=steps)

num_bins = 150
bins = np.linspace(-5, 5, num_bins)
hist = np.zeros(shape=(N, num_bins-1))
for i in range(N):
    hist[i], _ = np.histogram(xs[x_eq:,i], bins)
mean_hist = np.mean(hist, axis=0)

def integral(a, b, m, s):
    A = np.sqrt(2)*s**2
    return 0.5 * (erf((b-m)/A) - erf((a-m)/A))

C = N * steps
expected = steps * eq_f * np.array([integral(bins[i], bins[i+1], m, s)
                        for i in range(num_bins-1)])

with open('test.data', 'w') as f:
    for b, h, e in zip(bins, mean_hist, expected):
        f.write('{} {} {}\n'.format(b, h, e))

#SD = np.zeros(shape=(N, steps))
#for i in range(N):
#    SD[i] = [(xs[t,i]-xs[0,i])**2 for t in range(steps)]
#MSD = np.mean(SD, axis=0)
#with open('test.data', 'w') as f:
#    for t, m in enumerate(MSD):
#        f.write('{} {}\n'.format(t, m))
