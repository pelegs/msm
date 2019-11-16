#!/usr/bin/env /home/psapir/anaconda3/bin/python3.6
# -*- coding: iso-8859-15 -*-

import numpy as np
from sympy import *

x, A, m, a, b= symbols('a A mu a b')
p = exp(-(m-x)**2/2) + exp(-(m+x)**2/2)
U = -log(p)
U_1 = diff(U, x)
U_2 = diff(U_1, x)
UA = U_2.subs(x, m)
UB = U_2.subs(x, 0)

print(latex(simplify(UA)))
print(latex(simplify(UB)))

print(UA.subs(m, 3).evalf())
print(UB.subs(m, 3))
