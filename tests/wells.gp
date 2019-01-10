gauss(x, m, s, A) = A/sqrt(2*pi*s**2) * exp(-(x-m)**2/(2*s**2))
p(x, m1, s1, A1, m2, s2, A2) = 0.5 * (gauss(x, m1, s1, A1) + gauss(x, m2, s2, A2))
U(x, m1, s1, A1, m2, s2, A2) = -log(p(x, m1, s1, A1, m2, s2, A2))

set terminal gif animate delay 10
set output 'change_one_well_s.gif'

set xrange[-7:7]
set yrange[-1:15]

set sample 1000
m1 = -3
s1 = 1
A1 = 1
m2 = 3
s2 = 1

do for [i=1:500:10] {
    A2 = 0.1*i
    A2_str = sprintf("%0.1f", A2)
    set label "A2=".A2_str at graph 0.1,0.9
    plot U(x, m1, s1, A1, m2, s2, A2) lw 2 notitle
    unset label
}
