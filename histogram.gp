set terminal png size 1000,1000
set output 'data.png'

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

set table "tempfile" 
plot "data" u (bin($2, binwidth)):(1.0) smooth freq w boxes
unset table

stats "tempfile" u 1
set xrange[STATS_min:STATS_max]
binwidth = (STATS_max - STATS_min)/100
set boxwidth binwidth

stats "tempfile" u 2
plot "data" u (bin($2, binwidth)):(1.0/STATS_max) smooth freq w boxes notitle,\
	 U1(x) notitle
