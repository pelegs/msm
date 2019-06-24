#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import sys
import numpy as np
from numpy import exp, sqrt, pi, log
sqrt2pi = 1/sqrt(2*pi)


class potential:
    def __init__(self, a=1.0):
        self.a = a
        self.x_min = sqrt(1.0 / (2.0*a))

    def get_value(self, x):
        return self.a*x**4 - x**2

    def get_force(self, x):
        return 2*x * (1 - 2*self.a*x**2)


def is_transition(U, m, sign, x, kT_parameter=4):
    cond_energy1 = U.get_value([x]) <= U.get_value([0]) - kT_parameter
    if sign < 0:
        cond_sign = x >= 0
        cond_energy2 = x >= m
    else:
        cond_sign = x <= 0
        cond_energy2 = x <= -m
    return (cond_sign and cond_energy1) or cond_energy2


def simulate(params):
    num_steps = params['num_steps']
    num_dim = params['num_dim']
    num_particles = params['num_particles']
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    Xs = np.zeros(shape=(num_steps, num_dim, num_particles))
    Xs[0,:,:] = params['x0']
    for t in range(1, num_steps):
        drift = np.zeros(shape=(num_dim, num_particles))
        for i in range(num_particles):
            drift[:,i] = A * U.get_force(Xs[t-1,:,i])
        noise = B * np.random.normal(size=(num_dim, num_particles))
        Xs[t,:,:] = Xs[t-1,:,:] + drift + noise
    return Xs


def simulate_transitions_1D_no_memory(params, num_trans=100):
    """
    NOTE: At the moment only checks for the case
          of symmetric 1D double well and one particle.
    """
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    U0 = U.get_value(0)
    dt = params['Ddt']
    x_min = U.x_min
    KT_diff = params['KT_diff']
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

        # Condition for reseting the test (barrier crossing)
        if x >= x_min or (U.get_value(x) <= U0 - KT_diff and x > 0):
            transitions += 1
            times.append(t)
            x = x0
            print('\ra={:0.3f}, t={} trans={}'.format(U.a, t, transitions), end='')
    print('\r                                                          ', end='')
    delta_times = np.diff(times) / dt
    mean = np.mean(1.0 / delta_times)
    var = np.var(1.0 / delta_times)
    return mean, var

if __name__ == '__main__':
    # Get parameters
    m = float(sys.argv[1])
    num_trans = int(sys.argv[2])

    # Potential
    gaussians = []
    gaussians.append(gaussian(A=np.ones(1),
                              M=np.array([-m]),
                              S=np.ones(1)))
    gaussians.append(gaussian(A=np.ones(1),
                              M=np.array([m]),
                              S=np.ones(1)))
    U = potential(gaussians)

    # Parameters
    parameters = {
        'name': 'equilibrium_test',
        'num_dim': 1,
        'num_particles': 1,
        'KBT': 1,
        'Ddt': 0.01,
        'x0': np.array([[-m]]),
        'potential': U
    }

    # Simulation
    mean, err_min, err_max = simulate_transitions_1D_no_memory(parameters, num_trans=num_trans)
    #print 'Finished'

    # Write to file
    with open('data/kramer_par.data', 'a') as f:
        f.write('{} {} {} {}\n'.format(m, mean, err_min, err_max))
