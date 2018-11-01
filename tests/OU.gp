k = 10 
x0 = 0.5
D = 1.0
f(x, t) = sqrt(k/(2*pi*D*(1-exp(-2*k*t)))) * exp((-k/(2*D) * (x-x0*exp(-k*t))**2/(1-exp(-2*k*t))))
g(x, t) = sqrt(k/(2*pi*D)) * exp(-k*x**2/(2*D))

set pm3d
set samples 150
set isosamples 150
set yrange [0:1]
splot f(x, y) notitle
