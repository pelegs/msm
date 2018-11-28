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
        #numen += (M[i]-x)/S[i]**2 * gauss(x, M[i], S[i])
        #denom += denom + gauss(x, M[i], S[i])
        numen = x
        denom = 1.0

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
        F[i] = 1.0#multi_gauss(xs[i], M, S, beta)

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


# ------------------ Simulate histogram ------------------ #

cdef np.ndarray[double, ndim=1] c_simulate_hist(np.ndarray[double, ndim=1] x0s,
                                                np.ndarray[double, ndim=1] bins,
                                                np.ndarray[double, ndim=1] M,
                                                np.ndarray[double, ndim=1] S,
                                                double D, double beta,
                                                double dt, int total_steps,
                                                int step_block, int eq_time):

    cdef int a
    cdef int N = len(x0s)

    cdef int num_blocks = total_steps // step_block
    cdef np.ndarray[double, ndim=2] xs = np.zeros(shape=(step_block, N)).astype(np.float64)

    xs[0] = x0s
    cdef A = D * beta * dt
    cdef B = sqrt(2*D*dt)
    cdef np.ndarray[double, ndim=1] drift
    cdef np.ndarray[double, ndim=1] noise

    cdef np.ndarray[double, ndim=2] hist = np.zeros(shape=(step_block, len(bins[:-1])))
    cdef np.ndarray[double, ndim=2] mean_hist_block = np.zeros(shape=(num_blocks, len(bins[:-1])))
    cdef np.ndarray[double, ndim=1] mean_hist = np.zeros(len(bins[:-1]))

    cdef np.ndarray[double, ndim=1] X_axis = np.linspace(-5,5,N)

    cdef int i
    cdef int n
    for block in tqdm(range(num_blocks)):
        if block > 0:
            xs_last = xs[-1]
            xs = np.zeros(shape=(step_block, N)).astype(np.float64)
            xs[0] = xs_last
        for i in range(1, step_block):
            drift = cgaussian_force(X_axis, M, S, beta) * A
            noise = np.random.normal(0, 1, N) * B
            xs[i] = 0.0#xs[i-1] +  drift + noise
            mean_hist = np.histogram(drift, bins)
    cdef double area = np.sum(mean_hist)
    return mean_hist / area

def simulate_hist(x0s, bins,
                  M=[0], S=[1], D=1, beta=1, dt=0.01,
                  total_steps=1000, step_block=100, eq_time=100):
    return c_simulate_hist(x0s, bins, M, S, D, beta, dt, total_steps, step_block, eq_time)
