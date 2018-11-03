set grid
set size square
set title 'MSD-Slope from 100 Particles vs. Expected Slope'
set xlabel '$2\cdot D$'
set ylabel 'MSD-Slope'
set key left

f(x) = a*x + b
fit f(x) "slopes.data" u 1:2 via a,b
set terminal cairolatex standalone pdf color colortext
set output "plot.tex"
plot a*x+b lw 30 lc rgb "#CC00FF00" title "Linear fit",\
     "slopes.data" u 1:2 pt 7 ps 0.5 lc rgb "#770000FF" title "Langevin",\
     "slopes.data" u 1:3 pt 2 ps 0.5 lc rgb "#77FF0000" title "Smoluchowski"
