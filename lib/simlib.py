#!/usr/bin/env python3

import numpy as np
from tqdm import tqdm

class gaussian:
    def __init__(self, center=0.0, stdev=1.0):
        self.m = center
        self.s = stdev
        #self.a = amplitude

    def get_value(self, x):
        #return 1/(self.s*np.sqrt(2*np.pi)) * np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))
        return np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))

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
             dstep = 1.0, D = 1.0, beta=1.0, x0 = 0.0):
    """
    Actuall simulation.
    More details to come.
    """

    C1 = D * beta * dt
    C2 = np.sqrt(2*D*dt)

    ts = np.arange(0, max_t, dt)
    xs = np.ones(shape=(len(ts), num_particles)) * x0
    vs = np.zeros(len(ts))

    for i, t in enumerate(tqdm(xs[:-1])):
        for j, x in enumerate(t):
            if method in ['lang', 'langevin']:
                xs[i+1][j] = x + C1 * potential.get_force(x) + C2 * np.random.normal()
            elif method in ['smol', 'smlouchowski']:
                c = potential.get_derivative(x)
                mu = x - C1*c
                xs[i+1][j] = np.random.normal(mu, C2)
            else:
                raise ValueError('Unknown method \'{}\''.format(method))

    return ts, xs

def print_simulate(name,
                   potential, method = 'langevin',
                   max_t = 1000, dt = 0.1,
                   num_particles = 1, num_bins = 20,
                   dstep = 1.0, D = 1.0, beta=1.0, x0 = 0.0):

    print('''Now starting simulation '{}', with the following parameters:
method: {}
number of particles = {}
maximum time = {}, dt = {}
k = {}, D = {}, beta = {}, x0 = {}'''.format(name,
                                             method,
                                             num_particles,
                                             max_t, dt,
                                             potential.k, D, beta, x0)
          )

    C1 = D * beta * dt
    C2 = np.sqrt(2*D*dt)

    sqrt_N = np.sqrt(num_particles)

    xs = np.ones(num_particles) * x0
    xs_prev = np.ones(num_particles) * x0
    ts = np.arange(0, max_t, dt)

    real_mean = x0 * np.exp(-potential.k*D*beta*ts)
    real_var  = 1/(potential.k*beta) * (1-np.exp(-2*potential.k*D*beta*ts))

    filename = '../data/{}_{}_D_{}_k_{}_beta_{}_x0_{}.data'.format(name, method, D, potential.k, beta, x0)
    with open(filename, 'wb', 0) as f:
        line = '# Num particles: {}, x0={}, D={}, beta={}, k={}\n'.format(num_particles,
                                                                          x0, D, beta,
                                                                          potential.k)
        f.write(line.encode())

        for i, t in enumerate(tqdm(ts[:-1])):
            for j in range(num_particles):
                if method in ['lang', 'langevin']:
                    xs[j] = xs_prev[j] + C1 * potential.get_force(xs_prev[j]) + C2 * np.random.normal()
                    xs_prev[j] = xs[j]
                elif method in ['smol', 'smlouchowski']:
                    c = potential.get_derivative(xs_prev[j])
                    mu = xs_prev[j] - C1*c
                    xs[j] = np.random.normal(mu, C2)
                    xs_prev[j] = xs[j]
                else:
                    raise ValueError('Unknown method \'{}\''.format(method))

            m = np.mean(xs)
            dm = np.std(xs) / sqrt_N
            v = np.var(xs)
            dv = 2/(num_particles-1) * np.var(xs)**2

            line = '{} {} {} {} {} {} {}\n'.format(t,
                                                   m, dm, real_mean[i],
                                                   v, dv, real_var[i])
            f.write(line.encode())

def MSD(xs):
    return [np.mean([(xs[t+1,i] - xs[0,i])**2 for i,_ in enumerate(xs[t,:])])
                                              for t,_ in enumerate(xs[:-1,0])]
