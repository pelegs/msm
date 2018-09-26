#!/usr/bin/env bash

for amp in "$@"
do
  printf %"s1 1000000 1 1 1 $amp 5 1\n-5 1 1\n5 1 1" > simulation/double_well_KT="$amp"
done
