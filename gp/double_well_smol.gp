set size square
set xlabel "x"
set ylabel "p(x)"
set grid

stats "data/double_well_smol.data" u 2
xmin = STATS_min
xmax = STATS_max

binwidth = (xmax-xmin) / 200
bin(x,width)=width*floor(x/width)
stats "data/double_well_smol.data" using 2
sum = STATS_records

#set terminal cairolatex standalone pdf color colortext
#set output "graphs/double_well_smol.tex"
set term pngcairo size 1200,1200
set output "graphs/double_well_smol.png"
set style fill solid 0.5
set xrange[xmin:xmax]
#set yrange[0:1.1]
plot "data/double_well_smol.data" using (bin($2,binwidth)):(1.0/(binwidth*sum)) smooth freq with boxes lc rgb "#35BB99" title "Calculated P",\
     "data/double_well_smol.data" using 2:3 pt 7 ps 0.5 lc rgb "#FF0000" title "Expected P"
