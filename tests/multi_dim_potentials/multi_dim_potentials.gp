gauss(x, m, s) = 1/(sqrt(2*pi)*s) * exp(-(x-m)**2/(2*s**2))
gauss2d(x, y, mx, my, sx, sy) = 0.5 * gauss(x, mx, sx) * gauss(y, my, sy)
g(x, y) = gauss2d(x, y, -5, 2, 1, 1) + gauss2d(x, y, 5, 2, 1, 1) + gauss2d(x, y, 0, 5, 1, 1) + 10*gauss2d(x, y, 0, -3, 4, 4)
U(x, y) = -log(g(x, y))

set pm3d map
set xrange [-10:10]
set yrange [-10:10]
set isosample 200, 200
set size square

set multiplot layout 1,2
splot g(x, y) notitle
splot U(x, y) notitle
unset multiplot
