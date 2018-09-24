set size square
set grid
set xlabel "x"
set ylabel "y"

Gauss(x, m, s, a) = a * exp(-(x-m)**2/(2*s**2))

set xrange[-20:20]
plot for [i=1:10] -i*log(Gauss(x, -5, 1, 1) + Gauss(x, 5, 1, 1)) notitle
