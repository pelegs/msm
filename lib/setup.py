#!/usr/bin/env python3

from distutils.core import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize("libsim.pyx", annotate=True),
    include_dirs=[np.get_include()]
)
