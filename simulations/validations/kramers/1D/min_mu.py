#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
from numpy import sqrt, log, arange
import sys


def min_mu(a):
    return sqrt(2*(a+log(2)))


max_a = int(sys.argv[1])
aa = arange(1, max_a+1, 1)
for a in aa:
    print(a, min_mu(a))
