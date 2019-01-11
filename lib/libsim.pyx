import numpy as np
cimport numpy as np
from libc.math cimport sqrt, exp, log, pi
from tqdm import tqdm


# ------------------ Gaussian force ------------------ #

cdef double gauss(double x, double m, double s):
    return 1/(sqrt(2*pi)*s) * exp(-(x-m)**2/(2*s**2))

cdef double multi_gauss(double x,
                        np.ndarray[double, ndim=1] M,
                        np.ndarray[double, ndim=1] S,
                        double beta):
    cdef double b_ = 1/beta
    cdef double numen = 0.0
    cdef double denom = 0.0
    cdef int k = len(M)

    for i in range(k):
        numen += (M[i]-x)/S[i]**2 * gauss(x, M[i], S[i])
        denom += gauss(x, M[i], S[i])

    return b_*numen/denom


cdef np.ndarray[double, ndim=1] cgaussian_force(np.ndarray[double, ndim=1] xs,
                                                np.ndarray[double, ndim=1] M,
                                                np.ndarray[double, ndim=1] S,
                                                double beta):
    cdef int N = len(xs)
    cdef np.ndarray[double, ndim=1] F = np.zeros(N)

    cdef int i
    for i in range(N):
        F[i] = multi_gauss(xs[i], M, S, beta)

    return F


# ------------------ Simulate function ------------------ #

cdef int c_simulate(str name,
                    np.ndarray[double, ndim=1] x0s,
                    np.ndarray[double, ndim=1] M,
                    np.ndarray[double, ndim=1] S,
                    double D, double beta,
                    double dt, int total_steps):

    cdef int num_particles = len(x0s)
    cdef np.ndarray[double, ndim=1] xs = np.zeros(num_particles).astype(np.float64)

    cdef double A = D * beta * dt
    cdef double B = sqrt(2*D*dt)

    cdef str xs_str = ''
    cdef int i
    with open('../data/{}.data'.format(name), 'w') as f:
        for i in tqdm(range(total_steps)):
            drift = A * cgaussian_force(xs, M, S, beta)
            noise = B * np.random.normal(0, 1, num_particles)
            xs += drift + noise
            xs_str = ' '.join(map(str, xs))
            f.write('{}\n'.format(xs_str))

    return 0

def simulate(name, x0s, M=0.0, S=1.0, D=1.0, beta=1.0, dt=0.01, total_steps=1000):
    c_simulate(name, x0s, M, S, D, beta, dt, total_steps)
    return 0

# ------------------ Simulate histogram ------------------ #

cdef np.ndarray[long, ndim=2] c_simulate_histogram(int num_particles,
                                                   int random, double xmin, double xmax, double x0,
                                                   np.ndarray[double, ndim=1] bins,
                                                   np.ndarray[double, ndim=1] M,
                                                   np.ndarray[double, ndim=1] S,
                                                   double D, double beta,
                                                   double dt, int total_steps, int equilibration_time):

    cdef np.ndarray[double, ndim=1] x = np.zeros(total_steps)
    x[0] = x0

    cdef int t, i

    cdef double A = D * beta * dt
    cdef double B = sqrt(2*D*dt)

    cdef int num_bins = len(bins)-1
    cdef np.ndarray[long, ndim=2] hist = np.zeros(shape=(num_particles, num_bins)).astype(int)

    cdef np.ndarray[double, ndim=1] x0s
    if random:
        x0s = np.random.uniform(xmin, xmax, size=num_particles)
    else:
        x0s = np.ones(num_particles).astype(np.float64)

    for i in tqdm(range(num_particles)):
        for t in range(1, total_steps):
            drift = A * multi_gauss(x[t-1], M, S, beta)
            noise = B * np.random.normal(0, 1)
            x[t] = x[t-1] + drift + noise
        hist[i], _ = np.histogram(x[equilibration_time:], bins)

    return hist

def simulate_histogram(num_particles=100,
                       random=0, xmin=0, xmax=0, x0=0.0,
                       bins=np.linspace(-5, 5, 100),
                       M=[0], S=[1],
                       D=1, beta=1,
                       dt=0.001, total_steps=1000, equilibration_time=0):
    return c_simulate_histogram(num_particles,
                                random, xmin, xmax, x0,
                                bins,
                                M, S,
                                D, beta,
                                dt, total_steps, equilibration_time)
