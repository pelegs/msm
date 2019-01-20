set terminal cairolatex standalone pdf color colortext header '\newcommand{\hl}[1]{\setlength{\fboxsep}{0.75pt}\colorbox{white}{#1}}'
set output "gauss.tex"

set xlabel '$x$'
set ylabel '$U\left(x\right)$'

set sample 1000
set xrange[-6:6]

gauss(x, m, s, A) = A * exp(-(x-m)**2/(2*s**2))
p(x,M,d) = gauss(x, M-d, 0.05, 1) + gauss(x, M, 0.05, 1) + gauss(x, M+d, 0.05, 1) 
U(x) = -log(p(x,-4,0.5) + p(x,4,1))

plot U(x) lw 2 lc rgb "red" notitle
