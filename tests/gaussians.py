#!/usr/bin/env python3

def gauss(A, m, s):
    return '{}*exp(-(x-{})**2/(2*{}**2))'.format(A, m, s)

def dg(A, m, s):
    return '-1 * ' + gauss(A, m, s) + '*(x-{})/{}**2'.format(m, s)

def U(gs):
    return '-log({})'.format('+'.join(gs))

def dU(gs, dgs):
    return '-({})/({})'.format('+'.join(dgs), '+'.join(gs))

G0 = gauss(1, -2, 1)
G1 = gauss(1, +2, 1)

dG0 = dg(1, -2, 1)
dG1 = dg(1, +2, 1)

gs = [G0, G1]
dgs = [dG0, dG1]

print(U(gs))
print(dU(gs, dgs))
