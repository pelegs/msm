import numpy as np
cimport numpy as np
from libc.math cimport sqrt, exp, log, pi
from tqdm import tqdm

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

cdef double gauss(double x, double m, double s):
    return 1/(sqrt(2*pi)*s) * exp(-(x-m)**2/(2*s**2))

cdef np.ndarray[DTYPE_t, ndim=1] cgaussian_force(np.ndarray[DTYPE_t, ndim=1] xs,
                                                 double m, double s, double beta):
    cdef int N = len(xs)
    cdef double A
    cdef double B = 1/beta
    cdef np.ndarray[DTYPE_t, ndim=1] F = np.zeros(N)
    cdef int i
    for i in range(N):
        F[i] = B * (m-xs[i])/s**2
    return F

def gaussian_force(xs, m=0, s=1, b=1):
    return cgaussian_force(xs, m, s, b)

cdef np.ndarray[DTYPE_t, ndim=2] cmove(np.ndarray[DTYPE_t, ndim=1] x0s,
                                       double m, double s,
                                       double D, double beta,
                                       double dt, int steps):

    cdef int a
    cdef int N = len(x0s)
    cdef np.ndarray[DTYPE_t, ndim=2] xs = np.zeros(shape=(steps, N)).astype(np.float64)
    xs[0] = x0s
    cdef A = D * beta * dt
    cdef B = sqrt(2*D*dt)

    cdef int i
    for i in tqdm(range(1, steps)):
        xs[i] = xs[i-1] + cgaussian_force(xs[i-1], m, s, beta) * A + np.random.normal(m, s, N) * B

    return xs

def move(x0s, m=0, s=1, D=1, beta=1, dt=0.01, steps=1000):
    return cmove(x0s, m, s, D, beta, dt, steps)
