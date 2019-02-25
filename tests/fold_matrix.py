#!/usr/bin/env python3

import numpy as np


def matrix_range(min, max, shape):
    matrix = np.zeros(shape)
    array = np.linspace(min, max, shape[0]*shape[1])
    for i in range(shape[0]):
        matrix[i] = array[i*shape[1]:i*shape[1]+shape[1]]
    return matrix

bla = matrix_range(0, 499, (100,5))
print(bla)
