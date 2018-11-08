#!/usr/bin/env python3

import numpy as np


class gaussian:
    def __init__(self, center=0.0, stdev=1.0, amplitude=1.0):
        self.m = center
        self.s = stdev
        #self.a = amplitude

    def get_value(self, x):
        return 1/(self.s*np.sqrt(2*np.pi)) * np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))

    def get_derivative(self, x):
        return -self.get_value(x) * (x-self.m)/self.s**2


class potential:
    def __init__(self, type):
        self.type = type

    def get_force(self, x):
        return -self.get_derivative(x)

    def get_expected_probability(self, x, KT=1.0):
        return np.exp(-self.get_value(x)/KT)


class zero_potential(potential):
    def __init__(self):
        potential.__init__(self, type='zero')

    def get_value(self, x):
        return 0.0

    def get_derivative(self, x):
        return 0.0


class gaussian_potential(potential):
    def __init__(self, gaussians):
        potential.__init__(self, type='gaussian')
        self.gaussians = gaussians

    def get_sum_gaussians(self, x):
        return np.sum([gauss.get_value(x) for gauss in self.gaussians])

    def get_sum_gaussians_derivatives(self, x):
        return np.sum([gauss.get_derivative(x) for gauss in self.gaussians])

    def get_value(self, x):
        return -np.log(self.get_sum_gaussians(x))

    def get_derivative(self, x):
        numerator = self.get_sum_gaussians_derivatives(x)
        denominator = self.get_sum_gaussians(x)
        return -numerator / denominator


class harmonic_potential(potential):
    def __init__(self, m=0, k=1):
        potential.__init__(self, type='harmonic')
        self.m = m
        self.k = k

    def get_value(self, x):
        return 0.5 * self.k * (x-self.m)**2

    def get_derivative(self, x):
        return self.k * (x-self.m)


def simulate(potential, method = 'langevin',
             max_t = 1000, dt = 0.1,
             num_particles = 1, num_bins = 20,
             dstep = 1.0, D = 1.0, KT=1.0, x0 = 0.0,
             drift = True, noise = True):
    """
    Actuall simulation.
    More details to come.
    """

    C1 = D / KT * dt
    C2 = np.sqrt(2*D*dt)
    beta = 1/KT
    C3 = D * beta * dt

    ts = np.arange(0, max_t, dt)
    xs = np.ones(shape=(len(ts), num_particles)) * x0

    for i, t in enumerate(xs[:-1]):
        for j, x in enumerate(t):
            if method in ['lang', 'langevin']:
                vdt = 0.0
                if drift:
                    vdt += C1 * potential.get_force(x)
                if noise:
                    vdt += C2 * np.random.normal()
                xs[i+1][j] = x + vdt
            elif method in ['smol', 'smlouchowski']:
                c = potential.get_derivative(x)
                mu = x - C3*c
                xs[i+1][j] = np.random.normal(mu, C2)
            else:
                raise ValueError('Unknown method \'{}\''.format(method))

    hist = []
    bin_edges = []
    for i, positions in enumerate(xs[1:-1]):
        h, b = np.histogram(positions, bins=num_bins, density=True)
        hist.append(h)
        bin_edges.append(b)

    return ts, xs, np.array(hist), np.array(bin_edges)

def MSD(xs):
    return [np.mean([(xs[t+1,i] - xs[0,i])**2 for i,_ in enumerate(xs[t,:])])
                                              for t,_ in enumerate(xs[:-1,0])]
