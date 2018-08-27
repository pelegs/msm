set size square
set xrange[-8:8]
set xlabel "x"
set ylabel "p(x)"
set grid

binwidth=0.1
bin(x,width)=width*floor(x/width)

set table "temp"
plot "data/triple_well.data" using (bin($2,binwidth)):(1.0) smooth freq with boxes notitle
stats "temp" u 2
m = STATS_max
unset table

set term png size 1200,1200
set output "graphs/triple_well.png"
set style fill solid 0.5
plot "data/triple_well.data" using (bin($2,binwidth)):(1.0/m) smooth freq with boxes notitle
