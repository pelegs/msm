set size square
set grid
set xlabel "x"
set ylabel "y"

Gauss(x, m, s, a) = a * exp(-(x-m)**2/(2*s**2))

set xrange[-20:20]
plot for [i=0:50:10] -log(Gauss(x, -i, 1, 1) + Gauss(x, i, 1, 1)) notitle
