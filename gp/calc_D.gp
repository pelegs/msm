set print '-'
do for [j=1:50:1] {
    i = sprintf("%01.1f", j*0.1)
    f(x) = a*x
    fit f(x) "../data/no_potential_langevin_D_".i.".data" u 1:4 via a
    a_langevin = a
    fit f(x) "../data/no_potential_smol_D_".i.".data" u 1:4 via a
    a_smol = a
    m = 0.2*j
    text = sprintf("%f %f %f", m, a_langevin, a_smol)
    print(text)
}
