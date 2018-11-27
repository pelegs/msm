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
        denom += denom + gauss(x, M[i], S[i])

    return b_ * numen / denom


cdef np.ndarray[double, ndim=1] cgaussian_force(np.ndarray[double, ndim=1] xs,
                                                np.ndarray[double, ndim=1] M,
                                                np.ndarray[double, ndim=1] S,
                                                double beta):
    cdef int N = len(xs)
    cdef double A
    cdef np.ndarray[double, ndim=1] F = np.zeros(N)

    cdef int i
    for i in range(N):
        F[i] = multi_gauss(xs[i], M, S, beta)

    return F


# ------------------ Simulate function ------------------ #

cdef np.ndarray[double, ndim=2] csimulate(np.ndarray[double, ndim=1] x0s,
                                          np.ndarray[double, ndim=1] M,
                                          np.ndarray[double, ndim=1] S,
                                          double D, double beta,
                                          double dt, int steps):

    cdef int a
    cdef int N = len(x0s)
    cdef np.ndarray[double, ndim=2] xs = np.zeros(shape=(steps, N)).astype(np.float64)
    xs[0] = x0s
    cdef A = D * beta * dt
    cdef B = sqrt(2*D*dt)
    cdef np.ndarray[double, ndim=1] drift
    cdef np.ndarray[double, ndim=1] noise

    cdef int i
    for i in tqdm(range(1, steps)):
        drift = cgaussian_force(xs[i-1], M, S, beta) * A
        noise = np.random.normal(0, 1, N) * B
        xs[i] = xs[i-1] +  drift + noise

    return xs

def simulate(x0s, M=np.zeros(1), S=np.ones(1), D=1, beta=1, dt=0.01, steps=1000):
    return csimulate(x0s, M, S, D, beta, dt, steps)
