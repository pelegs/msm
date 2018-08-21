#!/usr/bin/env bash

name=$1
max_t=$2
action=$3

if [[ $action == "run" ]]
then
	python3 simulation/$name.py $max_t > data/$name.data && gnuplot gp/$name.gp && eog graphs/$name.png
elif [[ $action == "graph" ]]
then
    gnuplot gp/$name.gp && eog graphs/$name.png
else
    echo "$action is not a valid action!"
fi
