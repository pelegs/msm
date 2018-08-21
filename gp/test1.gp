set size square
set xrange[-10:10]
set xlabel "x"
set ylabel "p(x)"
set grid

binwidth=0.1
bin(x,width)=width*floor(x/width)

set table "temp"
plot "data/test1.data" using (bin($2,binwidth)):(1.0) smooth freq with boxes notitle
stats "temp" u 2
m = STATS_max
unset table

set term png size 1200,1200
set output "graphs/test1.png"
set style fill solid 0.5
plot "data/test1.data" u 2:3 w l lw 0.5 lc rgb "#3200FA" title "U(x)",\
     "data/test1.data" using (bin($2,binwidth)):(1.0/m) smooth freq with boxes notitle
