#!/usr/bin/env bash

for amp in "$@"
do
    printf %"s-10 1 $amp\n10 1 $amp" > "simulation/double_well_barrier_$amp.g"
done
