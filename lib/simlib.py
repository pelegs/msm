#!/usr/bin/env python3

import numpy as np
import sys

# For progress bar
from tqdm import tqdm

# Parsing arguments
def parse_cmdline_args():
    import argparse
    parser = argparse.ArgumentParser(description='Generating free energy landscapes from gaussian functions')
    parser.add_argument('--name', action='store', dest='name',
                        help='Simulation name',
                        type=str, default='default_name')
    parser.add_argument('-n', action='store', dest='num_particles',
                        help='Number of particles',
                        type=int, default=1)
    parser.add_argument('--maxt', action='store', dest='max_t',
                        help='Max time step',
                        type=int, default=1000)
    parser.add_argument('--dt', action='store', dest='dt',
                        help='Time step',
                        type=float, default=1.0)
    parser.add_argument('-E', action='store', dest='E',
                        help='Potential energy coefficient',
                        type=float, default=1.0)
    parser.add_argument('-D', action='store', dest='D',
                        help='Diffusion coefficient',
                        type=float, default=1.0)
    parser.add_argument('--KBT', action='store', dest='KBT',
                        help='Generalized energy',
                        type=float, default=1.0)
    args = parser.parse_args()
    return args

def set_parameters(args):
    global name
    global num_particles
    global max_t
    global dt
    global E
    global D
    global KBT
    global D_KBT
    global S2D

    name = args.name
    num_particles = args.num_particles
    max_t = args.max_t
    dt = args.dt
    E = args.E
    D = args.D
    KBT = args.KBT
    D_KBT = D/KBT
    S2D = np.sqrt(2*D*dt)

def parse_gaussians(gfile):
    with open(gfile, 'w') as f:
        lines = [line.rstrip('\n') for line in f]
    gaussians = [gaussian(center=float(params[0]), stdev=float(params[1]), amplitude=float(params[2]))
                 for line in lines
                 for params in line.split(' ')]
    return gaussians

class gaussian:
    def __init__(self, center=0.0, stdev=1.0, amplitude=1.0):
        self.m = center
        self.s = stdev
        self.a = amplitude

    def get_value(self, x):
        return self.a * np.exp(-(x-self.m)**2.0 / (2.0 * self.s**2.0))

class potential:
    def __init__(self, gaussians=[]):
        self.gaussians = gaussians

    def get_value(self, x):
        return -np.log(np.sum([gauss.get_value(x) for gauss in self.gaussians]))

    def get_force(self, x):
        val = np.sum([-g.get_value(x)*(x-g.m)/g.s**2.0 for g in self.gaussians])
        norm = np.sum([g.get_value(x) for g in self.gaussians])
        return val / norm * E

class particle:
    def __init__(self, x0=0):
        self.x = x0

    def move(self, u, dt, drift=True, noise=True):
        v = 0.0
        if drift:
            v += u.get_force(self.x) * D_KBT
        if noise:
            v += S2D * np.random.normal(0.0, 1.0)
        self.x += v

def run_simulation(particle_list, potential, t_max, name, drift=True, noise=True):
    with open('data/{}.data'.format(name), 'w', 1) as f:
        for t in tqdm(np.arange(0, t_max, dt)):
            sys.stderr.write('\rt={:3.4f} (of {:3.4f})   '.format(t, t_max))
            for particle in particle_list:
                particle.move(potential, dt, drift, noise)
            f.write('{} {}\n'.format(t,
                                     np.average([particle.x for particle in particle_list]),
                                     )
                    )


# Create global parameters
name = 'default_name'
num_particles = 1
max_t = 1
dt = 1.0
E = 1.0
D = 1.0
KBT = 1.0
D_KBT = 1.0
S2D = 1.0

# Parse and set parameters
args = parse_cmdline_args()
set_parameters(args)
