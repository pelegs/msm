set terminal cairolatex standalone pdf color colortext size 20cm, 45cm
set output "plot.tex"

if (!exists("MP_LEFT"))   MP_LEFT = .12
if (!exists("MP_RIGHT"))  MP_RIGHT = .95
if (!exists("MP_BOTTOM")) MP_BOTTOM = .03
if (!exists("MP_TOP"))    MP_TOP = .97
if (!exists("MP_GAP"))    MP_GAP = 0.05

set multiplot layout 3,1 margins screen MP_LEFT, MP_RIGHT, MP_BOTTOM, MP_TOP spacing screen MP_GAP

set macros
POS = "front at graph 0.03,0.92"
POS2 = "front at graph 0.03,0.82"

set style fill solid 1.0

set xlabel '\Huge$x$' offset 0,-1
set ylabel '\Huge Frequency' offset -2,0

set label '\huge$\mu=0,\sigma=1$' @POS
data1 = "../data/single_well.data"
set yrange [0:*]
plot data1 u 1:($2-$3):($2-$3):($2+$3):($2+$3) with candlesticks lc rgb "#DD0000FF" title "Simulation",\
     data1 u 1:4 pt 7 ps 0.2 lc rgb "blue" title "Theory"
unset label

set label '\huge$\mu=\pm2,\sigma=1$' @POS
data2 = "../data/double_well.data"
set yrange [0:*]
plot data2 u 1:($2-$3):($2-$3):($2+$3):($2+$3) with candlesticks lc rgb "#AA00BB00" title "Simulation",\
     data2 u 1:4 pt 7 ps 0.2 lc rgb "#00BB00" title "Theory"
unset label

set label '\huge$\mu=\left\{-5,0,5\right\}$' @POS
set label '\huge$\sigma=\left\{1,1,1\right\}$' @POS2
data3 = "../data/triple_well.data"
set yrange [0:*]
plot data3 u 1:($2-$3):($2-$3):($2+$3):($2+$3) with candlesticks lc rgb "#CCFF0000" title "Simulation",\
     data3 u 1:4 pt 7 ps 0.2 lc rgb "red" title "Theory"
unset label

#set yrange [0:90000]
#set label '\huge$\mu=\left\{-6,-3,0,3,6\right\}$' @POS
#set label '\huge$\sigma=\left\{1,0.9,0.8,0.9,0.8\right\}$' @POS2
#data4 = "../psapir/cython/quad_well.data"
#plot data4 u 1:2 pt 7 ps 0.4 lc rgb "#99AA00AA" title "Simulation",\
#     data4 u 1:3 with boxes lc rgb "#DDFF00FF" title "Theory"
#unset label
