#!/usr/bin/env bash

# =========== Parse arguments =========== #

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --name)
    NAME="$2"
    shift # past argument
    shift # past value
    ;;
    -n|--nump)
    NUMP="$2"
    shift # past argument
    shift # past value
    ;;
    --maxt)
    MAXT="$2"
    shift # past argument
    shift # past value
    ;;
    --dt)
    DT="$2"
    shift # past argument
    shift # past value
    ;;
    -E|--energy)
    ENERGY="$2"
    shift # past argument
    shift # past value
    ;;
    -D|--diffusion)
    DIFFUSION="$2"
    shift # past argument
    shift # past value
    ;;
    --kbt)
    KBT="$2"
    shift # past argument
    shift # past value
    ;;
    --action)
    ACTION="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# =========== Actual script =========== #

if [[ $ACTION == "run" ]]
then
    if [ ! -f data/$NAME.gp ]; then
          echo "Gnuplot script $NAME.gp not found, creating file"
          cp gp/base.gp gp/$NAME.gp
          sed "s/NAMEX/$NAME/g" gp/base.gp > gp/$NAME.gp
    fi
	  echo "Name: $NAME"
	  echo "Number of particles: $nump"
	  echo "Max time: $MAXP"
	  echo "Time step: $DT"
	  echo "Energy: $ENERGY"
	  echo "Diffusion coefficient: $DIFFUSION"
	  echo "Generalized temperature: $KBT"
    python3 simulation/simulate.py --name $NAME -n $NUMP --maxt $MAXT --dt $DT -E $ENERGY -D $DIFFUSION --KBT $KBT && gnuplot gp/$NAME.gp && eog graphs/$NAME.png

elif [[ $action == "graph" ]]
then
    if [ ! -f data/$NAME.gp ]; then
          echo "Gnuplot script $NAME.gp not found, creating file"
          cp gp/base.gp gp/$NAME.gp
          sed "s/NAMEX/$NAME/g" gp/base.gp > gp/$NAME.gp
    fi
    echo "Running gnuplot..."
    gnuplot gp/$NAME.gp && eog graphs/$NAME.png
else
    echo "$action is not a valid action!"
fi
