#!/bin/bash

source /etc/profile.d/modules.sh
module load shared

./kramers.py $1 2000 0.001 6

#$ -S /bin/bash
#$ -N kramers_parallel
#$ -l h_rt=24:0:0
#$ -cwd
#$ -pe *_fast 1
#$ -notify

trap "" TERM

set -o pipefail
