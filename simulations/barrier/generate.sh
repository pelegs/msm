#!/usr/bin/env bash

for i in $(seq -f "%0.2f" $1 $3 $2)
do
    cp base.sim dx_$i.sim
    sed -i 's/MX/'$i'/g' dx_$i.sim
    sed -i 's/AAA/'$i'/g' dx_$i.sim
done
