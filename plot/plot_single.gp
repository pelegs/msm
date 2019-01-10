set terminal cairolatex standalone pdf color colortext size 20cm, 20cm
set output "plot_single.tex"

set style fill solid 1.0

set xlabel '\Huge$x$' offset 0,-1
set ylabel '\Huge Frequency' offset -2,0

data = "../data/single_well.data"
set yrange [0:*]
plot data u 1:2 pt 7 ps 0.3 lc rgb "blue" title "Simulation",\
     data u 1:4 pt 7 ps 0.3 lc rgb "red" title "Theory"
