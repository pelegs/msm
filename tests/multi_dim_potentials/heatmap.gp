set palette rgb 33,13,10

set term png size 1200,1200
set output "heatmap.png"

set xlabel "x"
set ylabel "y"
set clabel "Counts"

set pm3d map
set size square
splot "multi_dim_potentials.data" matrix using (($1-20)*0.5):(($2-20)*0.5):3 title "2D Histogram"
