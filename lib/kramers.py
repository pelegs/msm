#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

import numpy as np
from numpy import exp, sqrt, pi, log
sqrt2pi = 1/sqrt(2*pi)


class gaussian():
    def __init__(self, A, M, S):
        if not A.shape == M.shape == S.shape:
            raise ValueError('Amplitude, Mean and Varience must have the same shape.')
            return
        self.A = A
        self.M = M
        self.S = S
        self.dim = A.shape[0]

    def get_1d_value(self, x, dim):
        a = self.A[dim]
        m = self.M[dim]
        s = self.S[dim]
        return a * sqrt2pi/s * exp(-(x-m)**2/(2*s**2))

    def get_1d_derivative(self, x, dim):
        a = self.A[dim]
        m = self.M[dim]
        s = self.S[dim]
        return (m-x)/s**2 * self.get_1d_value(x, dim)

    def get_partial_derivative(self, pos, dim):
        a = self.A[dim]
        m = self.M[dim]
        s = self.S[dim]
        return (m-pos[dim])/s**2 * self.get_value(pos)

    def get_value(self, pos):
        return np.prod([self.get_1d_value(x, i) for i, x in enumerate(pos)])


class potential:
    def __init__(self, gaussians, KBT=1):
        self.gaussians = gaussians
        self.num_dims = np.max([g.dim
                                for g in self.gaussians])
        self.KBT = KBT
        # Only relevant for one, 1D gaussian
        self.k = KBT / self.gaussians[0].S[0]**2

    def get_value(self, pos):
        val = np.sum([g.get_value(pos) for g in self.gaussians])
        return -self.KBT * np.log(val)

    def get_force(self, pos):
        # TODO: This needs to be properly vectorized
        norm_factor = self.KBT / np.sum([g.get_value(pos)
                                         for g in self.gaussians])
        force = np.zeros(self.num_dims)
        for d in range(self.num_dims):
            force[d] = np.sum([g.get_partial_derivative(pos, d)
                               for g in self.gaussians])
        return norm_factor * force

    def get_second_derivative(self, x):
        # NOTE: Currently only for 1D case with two
        #       symmetric wells
        m = self.gaussians[0].M[0]
        s = self.gaussians[0].S[0]
        num = s**2*exp(4*m*x/s**2) + (2*s**2-4*m**2)*exp(2*m*x/s**2) + s**2
        den = s**4*(exp(2*m*x/s**2)+1)**2
        return num/den


def simulate_transitions_1D_no_memory(params, num_trans=100, trans_dim=0):
    """
    NOTE: At the moment only checks for the case
          of symmetric 1D double well and one particle.
    """
    m = params['potential'].gaussians[1].M[0]
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    x0 = params['x0']
    x = x0
    t = 0
    transitions = 0
    times = [0]
    while transitions < num_trans:
        t += 1
        drift = A * U.get_force(x)
        noise = B * np.random.normal()
        x_old = x
        x = x + drift + noise
        if np.sign(x) != np.sign(x_old):
            transitions += 1
            x = x0
            times.append(t)
            print('\rm={:0.2f}: {} (of {}), t={}   '.format(m, transitions, num_trans, t), end='')
    delta_times = np.diff(times)
    mean = np.mean(1.0 / delta_times)
    var = np.var(1.0 / delta_times)
    #err_min = (transitions-2) / t * (1 - 1.96/sqrt(transitions))
    #err_max = (transitions-2) / t * (1 + 1.96/sqrt(transitions))
    return mean, var
