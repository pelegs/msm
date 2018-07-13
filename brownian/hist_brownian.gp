set terminal png size 1000,1000
set output "data_brownian.png"

#minX = -10
#maxX = 10
#set xrange[minX:maxX]

binwidth=.1 #(maxX-minX)/100
set boxwidth binwidth
bin(x, width) = width*floor(x/width) + binwidth/2.0

stats "data_brownian" u (bin($3, binwidth)):(1.0)
plot "data_brownian" u (bin($3, binwidth)):(1.0) smooth freq w boxes notitle
