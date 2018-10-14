c = 1
L(x) = c*x
D = 1
b = 1
dt = 0.01
t0 = 0
x0 = 0
A(x,t) = sqrt(4*pi*D*(t-t0))
B(x,t) = x-x0 + D*b*c*(t-t0)
C(x,t) = 4 * D * (t-t0)
p(x,t) = 1/A(x,t) * exp(-B(x,t)**2/C(x,t))

set term png size 1200,1200 font "Helvetica,20"
set xrange[-5:5]
set yrange[0:1]

frame = 0
do for [k=0:1000] {
    frame = frame + 1
    tau = t0 + k*dt
    outfile = sprintf("frames/smoluchowski_%04d.png", frame)
    set output outfile
    plot p(x,tau) notitle
}
