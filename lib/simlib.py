#!/usr/bin/env python3

import numpy as np
import sys

# For progress bar
from tqdm import tqdm


def parse_parameters_file(sim_name):
    with open('simulation/{}.g'.format(sim_name), 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    components = []
    for i, line in enumerate(lines):
        if i == 0:
            line_params = line.split(' ')
            parameters = {
                'num_particles': int(line_params[0]),
                'max_t': float(line_params[1]),
                'dt': float(line_params[2]),
                'dstep': float(line_params[3]),
                'E': float(line_params[4]),
                'g': float(line_params[5]),
                'KBT': float(line_params[6]),
                'x0': float(line_params[7]),
                'method': line_params[9]
            }
            parameters['D'] = parameters['KBT'] / parameters['g']
            parameters['g_']  = 1.0 / parameters['g']
            parameters['S2D'] = np.sqrt(2 * parameters['D'] * parameters['dt'])
        elif i == 1:
            line_params = line.split(' ')
            parameters['potential_type'] = line_params[0]
            parameters['drift'] = bool(int(line_params[1]))
            parameters['noise'] = bool(int(line_params[2]))
        else:
            if parameters['potential_type'] == 'gaussian':
                m, s, A = [float(x) for x in line.split(' ')]
                components.append(gaussian(m, s, A))
            elif parameters['potential_type'] == 'harmonic':
                components.append(float(line))
    return parameters, components


class gaussian:
    def __init__(self, center=0.0, stdev=1.0, amplitude=1.0):
        self.m = center
        self.s = stdev
        self.a = amplitude

    def get_value(self, x):
        return self.a * np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))

    def get_derivative(self, x):
        return -self.get_value(x) * (x-self.m)/self.s**2

class gaussian_potential:
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

    def get_expected_probability(self, x):
        return self.get_sum_gaussians(x)


class harmonic_potential:
    def __init__(self, parameters, k=1):
        self.parameters = parameters
        self.k = k[0]

    def get_value(self, x):
        return self.k * x**2

    def get_derivative(self, x):
        return 2 * self.k * x

    def get_expected_probability(self, x):
        return np.exp(-self.k * x**2 / (self.parameters['D']))

    def get_force(self, x):
        return -1 * self.get_derivative(x)

class particle:
    def __init__(self, parameters):
        self.parameters = parameters
        self.x = parameters['x0']
        self.msd = 0.0

        self.D = parameters['D']
        self.dt = parameters['dt']
        self.dist_sigma = np.sqrt(2*self.D*self.dt)
        self.beta = 1.0 / parameters['KBT']

    def move(self, u, dt, method='langevin', drift=True, noise=True):
        x_prev = self.x

        if method == 'langevin':
            vdt = 0.0
            if drift:
                vdt += u.get_force(self.x) * self.parameters['g_'] * self.parameters['dt']
            if noise:
                vdt += self.parameters['S2D'] * np.random.normal(0.0, 1.0)
            self.x += vdt
        elif method == 'smoluchowski':
            c = u.get_derivative(self.x)
            m = self.x - self.D * self.beta * c * self.dt
            self.x = np.random.normal(m, self.dist_sigma)
        else:
            raise ValueError('Unknown method \'{}\''.format(method))

        self.msd += (self.x - x_prev)**2


def run_simulation(sim_name, parameters, particle_list,
                   potential, drift=True, noise=True):
    drift_text, noise_text = 'with', 'with'
    if not drift:
        drift_text += 'out'
    if not noise:
        noise_text += 'out'
    info = '''
# Simulation: {}, with the following parameters:
# Number of particles = {}, x0 = {},
# max_t = {}, dt = {}, recording every {} steps,
# E = {}, gamma = {}, KBT = {} ==> D = {},
# Method: {}, {} drift, {} noise\n\n'''.format(
                         sim_name,
                         parameters['num_particles'], parameters['x0'],
                         parameters['max_t'], parameters['dt'], parameters['dstep'],
                         parameters['E'], parameters['g'], parameters['KBT'], parameters['D'],
                         parameters['method'], drift_text, noise_text
                        )
    sys.stderr.write(info)
    max_t = parameters['max_t']
    dt = parameters['dt']
    dstep = parameters['dstep']
    with open('data/{}.data'.format(sim_name), 'w', 1) as f:
        f.write(info)
        step = 0
        for t in tqdm(np.arange(0, max_t, dt)):
            for particle in particle_list:
                particle.move(potential, dt, method=parameters['method'], drift=drift, noise=noise)
            if step == dstep:
                avg_x = np.average([particle.x for particle in particle_list])
                avg_msd = np.average([particle.msd for particle in particle_list])
                f.write('{} {} {} {}\n'.format(t,
                                               avg_x,
                                               potential.get_expected_probability(avg_x),
                                               avg_msd,
                                               )
                       )
                step = 0
            step += 1
