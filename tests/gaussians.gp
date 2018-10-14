set size square
set grid
set xlabel "x"
set ylabel "y"

Gauss(x, m, s, a) = a * exp(-(x-m)**2/(2*s**2))
dG(x, m, s, a) = -Gauss(x, m, s, a) * (x-m)/(2*s)

G1(x) = Gauss(x, -2, 1, 1)
G2(x) = Gauss(x, 0, 0.5, 2)
G3(x) = Gauss(x, 1, 1, 1)

set xrange [-5:5]

U(x) = -log(G1(x) + G2(x) + G3(x))

plot U(x) notitle
