#!/usr/bin/env bash

for amp in "$@"
do
  filename=simulation/double_well_KT_${amp}.g
  printf %"s1 10000000 1 1 1 $amp 5 1\n-5 1 1\n5 1 1" > $filename
done
