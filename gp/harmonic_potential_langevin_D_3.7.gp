set size square
set xlabel "x"
set ylabel "p(x)"
set grid

stats "data/harmonic_potential_langevin_D_3.7_histogram.data" u 1
xmin = STATS_min
xmax = STATS_max

#set terminal cairolatex standalone pdf color colortext
#set output "graphs/harmonic_potential_langevin_D_3.7.tex"
set term pngcairo size 1200,1200
set output "graphs/harmonic_potential_langevin_D_3.7.png"
set style fill solid 0.5
set xrange[xmin:xmax]
#set yrange[0:1.1]
plot "data/harmonic_potential_langevin_D_3.7_histogram.data" using 1:2 smooth freq with boxes lc rgb "#35BB99" title "Calculated P",\
     "data/harmonic_potential_langevin_D_3.7.data" using 2:3 pt 7 ps 0.5 lc rgb "#FF0000" title "Expected P"
