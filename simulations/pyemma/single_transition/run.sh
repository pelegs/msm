#!/bin/bash

source /etc/profile.d/modules.sh
module load shared

./st2d_par.py $1 $2 $3 $4 $5 $6

#$ -S /bin/bash
#$ -l h_rt=24:0:0
#$ -cwd
#$ -pe *_fast 1
#$ -notify

trap "" TERM

set -o pipefail
