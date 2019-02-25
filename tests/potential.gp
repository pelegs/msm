filename = system("echo $filename")
z_var = system("echo $z_var")

set terminal png size 1000, 1000
set output filename

unset border
unset tics
unset key

set title "z = ".z_var

set pm3d map
splot "potential.data" u 1:2:4
