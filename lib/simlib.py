import numpy as np
from numpy import exp, sqrt, pi, log
sqrt2pi = 1/sqrt(2*pi)
from tqdm import tqdm_notebook, tqdm
import configparser
import sys


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
    x0 = np.array([float(x) for x in params['x0'].split(',')])
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

    return {
            'name': name,
            'num_steps': num_steps,
            'num_dim': num_dim,
            'beta': beta,
            'Ddt': Ddt,
            'x0': x0,
            'potential': U
            }


def save_trajectory_np(sim_name, Xs):
    np.save('../data/{}'.format(sim_name), Xs[:,:])


def simulate(params):
    num_steps = params['num_steps']
    num_dim = params['num_dim']
    num_particles = params['num_particles']
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    Xs = np.zeros(shape=(num_steps, num_dim, num_particles))
    Xs[0,:,:] = params['x0']
    for t in tqdm(range(1, num_steps)):
        drift = np.zeros(shape=(num_dim, num_particles))
        for i in range(num_particles):
            drift[:,i] = A * U.get_force(Xs[t-1,:,i])
        noise = B * np.random.normal(size=(num_dim, num_particles))
        Xs[t,:,:] = Xs[t-1,:,:] + drift + noise
    return Xs


def simulate_notebook(params):
    num_steps = params['num_steps']
    num_dim = params['num_dim']
    num_particles = params['num_particles']
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    Xs = np.zeros(shape=(num_steps, num_dim, num_particles))
    Xs[0,:,:] = params['x0']
    for t in tqdm_notebook(range(1, num_steps)):
        drift = np.zeros(shape=(num_dim, num_particles))
        for i in range(num_particles):
            drift[:,i] = A * U.get_force(Xs[t-1,:,i])
        noise = B * np.random.normal(size=(num_dim, num_particles))
        Xs[t,:,:] = Xs[t-1,:,:] + drift + noise
    return Xs


def simulate_equilibrium(params, binwidth,
                         equib_test=1000,
                         bound=0.99,
                         min_steps=10000,
                         max_steps=500000):
    """
    NOTE: At the moment only checks for the case
          of symmetric 1D double well and one particle.
    """
    num_steps = params['num_steps']
    num_dim = params['num_dim']
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    Xs = np.ones((1, 1)) * params['x0']
    x_neg = params['potential'].gaussians[0].M[0]
    x_pos = params['potential'].gaussians[1].M[0]
    bins = np.array([x_neg-binwidth, 0.0, x_pos+binwidth])
    bottom = bound
    top = 1.0/bound
    run = True
    t = 0
    while run and t < max_steps:
        t += 1
        drift = A * U.get_force(Xs[t-1])
        noise = B * np.random.normal()
        Xs_next = Xs[t-1] + drift + noise
        Xs = np.vstack((Xs, Xs_next))
        # Check equilibrium
        if t % equib_test == 0 and t >= min_steps:
            hist, _ = np.histogram(Xs.flatten(), bins)
            perc = float(hist[0]) / float(hist[1])
            if bottom <= perc <= top:
                run = False
            else:
                print('\r{} {} {:0.2f}'.format(t, hist, perc), end='')
        elif t < min_steps:
            print('\r{}   '.format(t), end='')
    print('')
    return Xs.flatten()


def simulate_transitions(params, num_trans=100, trans_dim=0):
    """
    NOTE: At the moment only checks for the case
          of symmetric 1D double well and one particle.
    """
    m = params['potential'].gaussians[1].M[0]
    num_steps = params['num_steps']
    num_dim = params['num_dim']
    A = params['Ddt'] / params['KBT']
    B = np.sqrt(2*params['Ddt'])
    U = params['potential']
    Xs = params['x0']
    t = 0
    transitions = 0
    while transitions < num_trans:
        t += 1
        drift = A * U.get_force(Xs[t-1,:])
        noise = B * np.random.normal(size=num_dim)
        Xs_next = Xs[t-1,:] + drift + noise
        Xs = np.vstack((Xs, Xs_next))
        if np.sign(Xs[t-1,trans_dim]) != np.sign(Xs[t,trans_dim]):
            transitions += 1
            print('\rm={:0.2f}: {} (of {}), t={}'.format(m, transitions, num_trans, t), end='')
    mean = float(transitions) / float(t)
    err_min = (transitions-2) / t * (1 - 1.96/sqrt(transitions))
    err_max = (transitions-2) / t * (1 + 1.96/sqrt(transitions))
    return Xs, mean, err_min, err_max


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


def simulate_transitions_1D_no_memory_poly(num_trans=100, a=0.1, x0=0):
    """
    NOTE: At the moment only checks for the case
          of symmetric 1D double well and one particle.
    """
    A = 0.001
    B = np.sqrt(2*0.01)
    x = x0
    t = 0
    transitions = 0
    while transitions < num_trans:
        t += 1
        drift = A * (-4*a*x**3 + 2*x)
        noise = B * np.random.normal()
        x_old = x
        x = x + drift + noise
        if np.sign(x) != np.sign(x_old):
            transitions += 1
            print('\ra={:0.2f}: {} (of {}), t={}   '.format(a, transitions, num_trans, t), end='')
    mean = float(transitions) / float(t)
    err_min = (transitions-2) / t * (1 - 1.96/sqrt(transitions))
    err_max = (transitions-2) / t * (1 + 1.96/sqrt(transitions))
    return mean, err_min, err_max
