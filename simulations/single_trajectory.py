#!/usr/bin/env python3

import numpy as np
from numpy import exp, sqrt, pi, log
sqrt2pi = 1/sqrt(2*pi)
from tqdm import tqdm
import configparser
import sys


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
            if den != 0:
                F[d] = nom / den
        return F

    def potential(self, pos):
        return -log(np.sum([np.prod([gaussian(pos[j], self.A[i,j], self.M[i,j], self.S[i,j]) for j in range(self.dim)])
                          for i in range(self.num_gaussians)]))


def load_data(config_file):
    # Load configurations
    config = configparser.ConfigParser()
    config.read(config_file)

    # Name
    name = config['NAME']['name']

    # General parameters
    params = config['PARAMETERS']
    num_steps = int(params['num_steps'])
    beta = float(params['beta'])
    Ddt = float(params['Ddt'])
    num_dim = int(params['num_dim'])
    num_gaussians = int(params['num_gaussians'])

    # Potential
    gaussians = [config['GAUSSIAN{}'.format(i)] for i in range(num_gaussians)]
    Amp = np.zeros(shape=(num_gaussians, num_dim))
    Mu  = np.zeros(shape=(num_gaussians, num_dim))
    Sig = np.zeros(shape=(num_gaussians, num_dim))
    for i, g in enumerate(gaussians):
        Amp[i] = [float(x) for x in g['Amp'].split(',')]
        Mu[i]  = [float(x) for x in g['Mu'].split(',')]
        Sig[i] = [float(x) for x in g['Sig'].split(',')]
    U = potential(Amp, Mu, Sig)

    return name, num_steps, num_dim, beta, Ddt, U

def two_dim_potential():
    U = potential(Amp, Mu, Sig)
    return U


def single_trajectory():
    out = '# Single trajectory\n'
    for t, x in enumerate(Xs[:,:]):
        out += '{}\n'.format(t, ' '.join(map(str, x)))
    return out


def save_trajectory_np(sim_name):
    np.save('../data/{}'.format(sim_name), Xs[:,:])


def main_sim(U, Xs):
    for t in tqdm(range(1, num_steps)):
        drift = A*U.force(Xs[t-1,:])
        noise = B*np.random.normal(size=num_dim)
        Xs[t,:] = Xs[t-1,:] + drift + noise

    return Xs

"""
SET PARAMS AND VARS
"""
name, num_steps, num_dim, beta, Ddt, U = load_data(sys.argv[1])
A = beta*Ddt
B = np.sqrt(2*Ddt)
Xs = np.zeros(shape=(num_steps, num_dim))

"""
SIMULATION
"""
Xs = main_sim(U, Xs)
save_trajectory_np(name)
