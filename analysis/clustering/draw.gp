set size square

set palette rgb 33, 13, 10
unset colorbox

set term png size 1200, 1200
set output "cluster.png"
plot "cluster.data" u 1:2:3 with points pt 7 ps 3 palette notitle
