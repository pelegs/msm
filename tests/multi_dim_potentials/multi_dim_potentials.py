#!/usr/bin/env python3

import numpy as np
from numpy import sqrt, exp, log, pi
sqrt2pi = 1/sqrt(2*pi)

def gaussian(x, a, m, s):
    return a * sqrt2pi/s * exp(-(x-m)**2/(2*s**2))

class potential:
    def __init__(self, A, M, S):
        self.dim = M.shape[1]
        self.num_gaussians = M.shape[0]
        self.A = A
        self.M = M
        self.S = S

    def force(self, pos):
        F = np.zeros(self.dim)
        for d, _ in enumerate(F):
            nom = np.sum([(self.M[i,d]-pos[d])/self.S[i,d]**2 * np.prod([gaussian(pos[j], self.A[i,j], self.M[i,j], self.S[i,j]) for j in range(self.dim)])
                          for i in range(self.num_gaussians)])
            den = np.sum([np.prod([gaussian(pos[j], self.A[i,j], self.M[i,j], self.S[i,j]) for j in range(self.dim)])
                          for i in range(self.num_gaussians)])
            F[d] = -nom / den
        return F

    def potential(self, pos):
        return -log(np.sum([np.prod([gaussian(pos[j], self.A[i,j], self.M[i,j], self.S[i,j]) for j in range(self.dim)])
                          for i in range(self.num_gaussians)]))


Amp = np.array([[1, 1],
                [1, 1],
                [1, 1]])
Mu  = np.array([[0, 5],
                [0, -5],
                [sqrt(3)*5, 0]])
Sig = np.array([[1, 1],
                [1, 1],
                [1, 1]])

U = potential(Amp, Mu, Sig)
xs = np.arange(-20, 20, 0.1)
ys = np.arange(-20, 20, 0.1)
xx, yy = np.meshgrid(xs, ys, sparse=True)
z = np.zeros(shape=(len(xs), len(ys)))
for i, x in enumerate(xs):
    for j, y in enumerate(ys):
        z[j,i] = U.potential([x, y])
for row in z:
    print(' '.join(map(str, row)))
