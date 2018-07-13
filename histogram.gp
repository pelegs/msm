set terminal png size 1000,1000

E=1
c=1000
c1=0.01
c2=0.2
dE = E/(4*c)
y_min = 1/sqrt(2*c)
U1(x)=(E*(c*x**4 - x**2) + dE)/dE
U2(x)=E*(c1*x**6 - c2*x**4 + x**2)

binwidth=0.1
set boxwidth binwidth
bin(x, width) = width*floor(x/width) + binwidth/2.0

set output 'data_position.png'
stats "data" u 2
set xrange[STATS_min:STATS_max]
binwidth = (STATS_max - STATS_min)/200
set boxwidth binwidth
plot "data" u (bin($2, binwidth)):(1.0/STATS_max) smooth freq w boxes notitle

set output 'data_velocity.png'
stats "data" u 3
set xrange[STATS_min:STATS_max]
binwidth = (STATS_max - STATS_min)/200
set boxwidth binwidth
plot "data" u (bin($3, binwidth)):(1.0/STATS_max) smooth freq w boxes notitle
