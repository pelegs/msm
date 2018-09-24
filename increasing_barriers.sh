#!/usr/bin/env bash

for amp in "$@"
do
    printf %"s1 1000000 1 1 1 $amp 5\n-5 1 1\n5 1 1" > "simulation/double_well_barrier_$amp.g"
done
