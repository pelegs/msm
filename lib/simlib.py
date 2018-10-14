#!/usr/bin/env python3

import numpy as np
import sys

# For progress bar
from tqdm import tqdm


def parse_parameters_file(sim_name):
    with open('simulation/{}.g'.format(sim_name), 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    gaussians = []
    for i, line in enumerate(lines):
        if i == 0:
            line_params =line.split(' ')
            parameters = {
                'num_particles': int(line_params[0]),
                'max_t': float(line_params[1]),
                'dt': float(line_params[2]),
                'E': float(line_params[3]),
                'g': float(line_params[4]),
                'KBT': float(line_params[5]),
                'x0': float(line_params[6]),
                'g_': 1.0 / float(line_params[4]),
                'S2D': np.sqrt(2 * float(line_params[5]) / float(line_params[4])),
            }
        else:
            m, s, A = [float(x) for x in line.split(' ')]
            gaussians.append(gaussian(m, s, A))
    return parameters, gaussians


class gaussian:
    def __init__(self, center=0.0, stdev=1.0, amplitude=1.0):
        self.m = center
        self.s = stdev
        self.a = amplitude

    def get_value(self, x):
        return self.a * np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))

    def get_derivative(self, x):
        return -self.get_value(x) * (x-self.m)/self.s**2

class potential:
    def __init__(self, parameters, gaussians):
        self.gaussians = gaussians
        self.parameters = parameters

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

    def get_force(self, x):
        return -self.parameters['E'] * self.get_derivative(x)


class particle:
    def __init__(self, parameters):
        self.parameters = parameters
        self.x = parameters['x0']

        self.D = parameters['KBT'] / parameters['g']
        self.dt = parameters['dt'] * 0.05
        self.dist_sigma = np.sqrt(2*self.D*self.dt)
        self.beta = 1.0 / parameters['KBT']

    def move(self, u, dt, method='langevin', drift=True, noise=True):
        if method == 'langevin':
            vdt = 0
            if drift:
                vdt += u.get_force(self.x) * self.parameters['g_']
            if noise:
                vdt += self.parameters['S2D'] * np.random.normal(0.0, 1.0)
            self.x += vdt
        elif method == 'smoluchowski':
            c = u.get_derivative(self.x)
            m = self.x - self.D * self.beta * c * self.dt
            self.x = np.random.normal(m, self.dist_sigma) * dt
        else:
            raise ValueError('Unknown method \'{}\''.format(method))


def run_simulation(sim_name, parameters, particle_list,
                   potential, drift=True, noise=True):
    sys.stderr.write('''
running simulation {}, with the following parameters:
number of particles = {}, x0 = {},
max_t = {}, dt = {},
E = {}, gamma = {},
KBT = {}\n\n'''.format(sim_name,
                       parameters['num_particles'], parameters['x0'],
                       parameters['max_t'], parameters['dt'],
                       parameters['E'], parameters['g'],
                       parameters['KBT']
                      )
                    )

    max_t = parameters['max_t']
    dt = parameters['dt']
    with open('data/{}.data'.format(sim_name), 'w', 1) as f:
        for t in tqdm(np.arange(0, max_t, dt)):
            for particle in particle_list:
                particle.move(potential, dt, method='langevin', drift=drift, noise=noise)

            f.write('{} {}\n'.format(t, np.average([particle.x for particle in particle_list])))
