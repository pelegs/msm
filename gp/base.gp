set size square
set xlabel "x"
set ylabel "p(x)"
set grid

stats "data/NAMEX_histogram.data" u 1
xmin = STATS_min
xmax = STATS_max

#set terminal cairolatex standalone pdf color colortext
#set output "graphs/NAMEX.tex"
set term pngcairo size 1200,1200
set output "graphs/NAMEX.png"
set style fill solid 0.5
set xrange[xmin:xmax]
#set yrange[0:1.1]
load "data/NAMEX_expected_probability.data"
plot "data/NAMEX_histogram.data" using 1:2 smooth freq with boxes lc rgb "#35BB99" title "Calculated P(x)",\
     p_exp(x) lw 3 lc rgb "#FF0000" title "Expected P(x)"
