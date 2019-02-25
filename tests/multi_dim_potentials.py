#!/usr/bin/env python3

import numpy as np
from numpy import exp, sqrt, pi, log
sqrt_2pi = 1/sqrt(2*pi)
from tqdm import tqdm
from subprocess import run
import os


def gauss(x, a, m, s):
    return a * sqrt_2pi/s * exp(-(x-m)**2/(2*s**2))

def gauss_axis(x, A, M, S):
    return np.sum([gauss(x, a, m, s) for a, m, s in zip(A, M, S)])

def potential(X, A, M, S):
    return np.prod([gauss_axis(x, A[dim], M[dim], S[dim])
                for dim, x in enumerate(X)])

Amp = np.array([[1, 1],
                [1, 1, 1],
                [1, 1]])
Mu  = np.array([[-5, 5],
                [-3, 0, 3],
                [-4, 4]])
Sig = np.array([[1, 1],
                [1, 1, 1],
                [1, 1]])

xs = np.arange(-7, 7, 0.2)
ys = np.arange(-7, 7, 0.2)
zs = np.arange(-7, 7, 0.1)

with open('potential.data', 'w') as f:
    for fnum, z in enumerate(tqdm(zs)):
        for x in xs:
            for y in ys:
                p = np.array([x, y, z])
                f.write('{} {}\n'.format(' '.join(map(str, p)), potential(p, Amp, Mu, Sig)))
            f.write('\n')
        run(['gnuplot', 'potential.gp'], env=dict(filename='frames/{:02d}.png'.format(fnum), z_var=str(z), **os.environ))
