set size square
set xlabel "x"
set ylabel "p(x)"
set grid

stats "data/no_potential_smol_D_0.6.data" u 2
xmin = STATS_min
xmax = STATS_max

binwidth = (xmax-xmin) / 200
bin(x,width)=width*floor(x/width)

set table "temp"
plot "data/no_potential_smol_D_0.6.data" using (bin($2,binwidth)):(1.0) smooth freq with boxes notitle
stats "temp" u 2
m = STATS_max
unset table

set term png size 1200,1200
set output "graphs/no_potential_smol_D_0.6.png"
set style fill solid 0.5
set xrange[xmin:xmax]
set yrange[0:1.1]
plot "data/no_potential_smol_D_0.6.data" using (bin($2,binwidth)):(1.0/m) smooth freq with boxes lc rgb "#35BB99" title "Calculated P",\
     "data/no_potential_smol_D_0.6.data" using 2:3 pt 7 ps 0.5 lc rgb "#FF0000" title "Expected P"
