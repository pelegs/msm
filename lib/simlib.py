import numpy as np
from numpy import exp, sqrt, pi, log
from scipy.special import erf
from scipy.stats import rv_continuous
from tqdm import tqdm_notebook, tqdm
import configparser
import sys
import pickle


sqrt2pi = sqrt(pi)
sqrt2 = sqrt(2)
s2p = sqrt(2*pi)


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
        return a * exp(-(x-m)**2/(2*s**2))

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

    def integral_1D(self, d, a, b):
        return 1/s2p * self.A[d]*self.S[d] * (erf((b-self.M[d])/(sqrt2*self.S[d])) - erf((a-self.M[d])/(sqrt2*self.S[d])))

    def integral(self, I):
        return np.prod([self.integral_1D(d, a, b) for d, (a, b) in enumerate(I)])


class potential:
    def __init__(self, gaussians=None, KBT=1):
        self.gaussians = gaussians
        if gaussians is not None:
            self.num_dims = np.max([g.dim
                                    for g in self.gaussians])
            self.num_gaussians = len(gaussians)
        else:
            self.num_gaussians = 0
        self.KBT = KBT

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

    def get_probability(self, x, dim=0):
        """
        Returns the probability of finding a particle
        at position x at equilibrium, using this potential.
        """
        norm = s2p * np.sum([gaussian.S[dim]*gaussian.A[dim] for gaussian in self.gaussians])
        integral = np.sum([gaussian.get_1d_value(x, dim) for gaussian in self.gaussians])
        return integral / norm

    def integral(self, intervals):
        if len(intervals) != self.num_dims:
            raise ValueError('Number of intervals ({}) is different than number of dimensions ({})!'.format(len(intervals), self.num_dims))
        return np.sum([ig.integral(intervals) for ig in self.gaussians])

    def get_theoretical_histogram(self, dim, bins, num_steps=1000):
        I = np.array([self.integral_1D(dim, bins[i], bins[i+1]) for i, b in enumerate(bins[:-1])])
        A = np.sum([g.A[dim]*g.S[dim] for g in self.gaussians])
        return I/A * num_steps

    def save(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, 'rb') as file:
            new = pickle.load(file)
            self.gaussians = new.gaussians
            self.num_dims = np.max([g.dim
                                    for g in self.gaussians])
            self.KBT = new.KBT


def create_starting_positions(potential, num_particles=1000,
                              xmin=-1, xmax=1):
    # Generate population
    population = np.linspace(xmin, xmax, num_particles)
    probability = np.array([potential.get_probability(x) for x in population])
    normalized_prob = probability / np.sum(probability)
    return np.random.choice(population, p=normalized_prob, size=num_particles)


class zero_potential(potential):
    def __init__(self):
        pass

    def get_force(self, pos):
        return pos * 0.0


def save_trajectory_np(sim_name, xs):
    np.save('../data/{}'.format(sim_name), xs[:,:])


def simulate(params, notebook=False):
    num_steps = params['num_steps']
    num_dim = params['num_dim']
    num_dim_sqrt = np.sqrt(num_dim)
    num_particles = params['num_particles']

    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']

    xs = np.zeros(shape=(num_steps, num_dim, num_particles))
    xs[0,:,:] = params['x0']

    if notebook:
        sim = tqdm_notebook(range(1, num_steps))
    else:
        sim = tqdm(range(1, num_steps))

    for t in sim:
        drift = np.zeros(shape=(num_dim, num_particles))
        for i in range(num_particles):
            drift[:,i] = A * U.get_force(xs[t-1,:,i])
        noise = B * np.random.normal(size=(num_dim, num_particles)) / num_dim_sqrt
        xs[t,:,:] = xs[t-1,:,:] + drift + noise
    return xs
