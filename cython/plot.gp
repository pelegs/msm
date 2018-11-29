set terminal cairolatex standalone pdf color colortext size 20cm, 60cm
set output "plot.tex"

if (!exists("MP_LEFT"))   MP_LEFT = .12
if (!exists("MP_RIGHT"))  MP_RIGHT = .95
if (!exists("MP_BOTTOM")) MP_BOTTOM = .03
if (!exists("MP_TOP"))    MP_TOP = .97
if (!exists("MP_GAP"))    MP_GAP = 0.035

set multiplot layout 4,1 margins screen MP_LEFT, MP_RIGHT, MP_BOTTOM, MP_TOP spacing screen MP_GAP

set macros
POS = "front at graph 0.03,0.92"
POS2 = "front at graph 0.03,0.82"

set style fill solid 1.0

set xlabel '\Huge$x$' offset 0,-1
set ylabel '\Huge Frequency' offset -2,0

set label '\huge$\mu=0,\sigma=1$' @POS
data1 = "single_well.data"
plot data1 u 1:2:(sqrt($2)) with yerror pt 7 ps 0.2 lc rgb "blue" title "Simulation",\
     data1 u 1:3 with boxes lc rgb "#DD0033FF" title "Theory"
unset label

set yrange [0:4500]
set label '\huge$\mu=\pm2,\sigma=1$' @POS
data2 = "double_well.data"
plot data2 u 1:2 pt 7 ps 0.2 lc rgb "#00AA22" title "Simulation",\
     data2 u 1:3 with boxes lc rgb "#DD00AA33" title "Theory"
unset label

set yrange [0:10500]
set label '\huge$\mu=\left\{-5,0,5\right\}$' @POS
set label '\huge$\sigma=\left\{1,1,1\right\}$' @POS2
data3 = "triple_well.data"
plot data3 u 1:2 pt 7 ps 0.4 lc rgb "red" title "Simulation",\
     data3 u 1:3 with boxes lc rgb "#DDFF0000" title "Theory"
unset label

set yrange [0:90000]
set label '\huge$\mu=\left\{-6,-3,0,3,6\right\}$' @POS
set label '\huge$\sigma=\left\{1,0.9,0.8,0.9,0.8\right\}$' @POS2
data4 = "../psapir/cython/quad_well.data"
plot data4 u 1:2 pt 7 ps 0.4 lc rgb "#99AA00AA" title "Simulation",\
     data4 u 1:3 with boxes lc rgb "#DDFF00FF" title "Theory"
unset label
