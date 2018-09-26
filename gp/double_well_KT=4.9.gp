set size square
set xlabel "x"
set ylabel "p(x)"
set grid

binwidth=0.1
bin(x,width)=width*floor(x/width)

stats "data/double_well_KT=4.9.data" u 2
xmin = STATS_min
xmax = STATS_max

set table "temp"
plot "data/double_well_KT=4.9.data" using (bin($2,binwidth)):(1.0) smooth freq with boxes notitle
stats "temp" u 2
m = STATS_max
unset table

set term png size 1200,1200
set output "graphs/double_well_KT=4.9.png"
set style fill solid 0.5
set xrange[xmin:xmax]
#set xrange[-10:10]
set yrange[0:1.1]
plot "data/double_well_KT=4.9.data" using (bin($2,binwidth)):(1.0/m) smooth freq with boxes notitle
