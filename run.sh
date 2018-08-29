#!/usr/bin/env bash

name=$1
num_particles=$2
max_t=$3
action=$4

if [[ $action == "run" ]]
then
    if [ ! -f data/$name.gp ]; then
          echo "Gnuplot script $name.gp not found, creating file"
          cp gp/base.gp gp/$name.gp
          sed "s/NAMEX/$name/g" gp/base.gp > gp/$name.gp
    fi
    echo "Running simulation $name, with $num_particles particles and max time $max_t"
	  python3 simulation/$name.py --name $name -n $num_particles --maxt $max_t && gnuplot gp/$name.gp && eog graphs/$name.png

elif [[ $action == "graph" ]]
then
    if [ ! -f data/$name.gp ]; then
          echo "Gnuplot script $name.gp not found, creating file"
          cp gp/base.gp gp/$name.gp
          sed "s/NAMEX/$name/g" gp/base.gp > gp/$name.gp
    fi
    echo "Running gnuplot..."
    gnuplot gp/$name.gp && eog graphs/$name.png
else
    echo "$action is not a valid action!"
fi
