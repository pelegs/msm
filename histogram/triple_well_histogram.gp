set terminal png size 1000,1000

binwidth=1
set boxwidth binwidth
bin(x, width) = width*floor(x/width) + binwidth/2.0

E = 0.25
c0 = 1
c1 = 0.2
c2 = 0.01
U1(x) = E*(c0*x**2 + c1*x**4)
U2(x) = E*(c0*x**2 - c1*x**4 + c2*x**6)

set output "png/triple_well.data_position.png"
stats "data/triple_well.data" u 2
set xrange[STATS_min:STATS_max]
binwidth = (STATS_max - STATS_min)/200

set table "temp"
plot "data/triple_well.data" u (bin($2, binwidth)):(1.0) smooth freq w boxes notitle
unset table
stats "temp" u 2
y_max = STATS_max

set xlabel "Position"
set ylabel "Normalized frequency"
set style fill solid 0.5
set yrange [0:1]
set sample 1000
set boxwidth binwidth
set style fill solid 0.25 noborder 
plot "data/triple_well.data" u (bin($2, binwidth)):(1.0/y_max) smooth freq w boxes lc rgb 0x0000AA00 title "Frequency",\
     U2(x) lw 3 lc rgb "#1E90FF" title "Potential"
