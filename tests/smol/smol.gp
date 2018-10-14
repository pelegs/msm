set grid

stat "smol.data"
sum=floor(STATS_records)
binwidth=(STATS_max-STATS_min)/50

set table "temp"
bin(x,width)=width*floor(x/width)
plot "smol.data" using (bin($1,binwidth)):(1.0) smooth freq
stats "temp" u 2
unset table

set style fill solid border -1
set term png size 1200,1200 font "Helvetica,30"
set output "smol.png"
plot "smol.data" using (bin($1,binwidth)):(1/(sum*binwidth)) smooth freq with boxes lc rgb "#67DE9F" title "Histogram",\
     "p.data" u 1:2 w l lw 3 lc rgb "#EB5E69" title "P(x)"
