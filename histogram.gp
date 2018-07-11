set terminal png size 1000,1000
set output 'data.png'

set xrange[-5:5]
set yrange[-0.25:2]
E=5
c=2
c1=0.01
c2=0.2
U1(x)=E*(c*x**4 - x**2)
U2(x)=E*(c1*x**6 - c2*x**4 + x**2)

binwidth=0.1
set boxwidth binwidth
bin(x, width) = width*floor(x/width) + binwidth/2.0
plot U1(x),\
     'data' u (bin($2, binwidth)):(1.0/(binwidth*1E5)) smooth freq w boxes
