#!/usr/bin/env bash

for amp in "$@"
do
    printf %"s1 10000 1 1 1 $amp 0\n0 1 1" > "simulation/flat_KT=$amp.g" 
done
