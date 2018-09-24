#set term png size 1200, 1200
f(x) = a*x
set print "-"
do for [i in "0.1 0.2 0.3 0.4 0.6 0.7 0.8 0.9"] {
    fit f(x) "../data/flat_KT=".i.".data" u 1:3 via a
    print("%d %d", i, a)
}
