#!/usr/bin/env bash

NAME=$1
ACTION=$2

if [[ $ACTION == "run" ]]
then
    if [ ! -f data/$NAME.gp ]; then
          echo "Gnuplot script $NAME.gp not found, creating file"
          cp gp/base.gp gp/$NAME.gp
          sed "s/NAMEX/$NAME/g" gp/base.gp > gp/$NAME.gp
    fi
    python3 simulation/simulate.py $NAME && gnuplot gp/$NAME.gp && eog graphs/$NAME.png

elif [[ $ACTION == "graph" ]]
then
    if [ ! -f data/$NAME.gp ]; then
          echo "Gnuplot script $NAME.gp not found, creating file"
          cp gp/base.gp gp/$NAME.gp
          sed "s/NAMEX/$NAME/g" gp/base.gp > gp/$NAME.gp
    fi
    echo "Running gnuplot..."
    gnuplot gp/$NAME.gp && eog graphs/$NAME.png
else
    echo "'$ACTION' is not a valid action :("
fi
