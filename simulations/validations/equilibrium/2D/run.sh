#!/bin/bash

source /etc/profile.d/modules.sh
module load shared

python2.7 equib_2d_par.py $1 $2 $3

#$ -S /bin/bash
#$ -l h_rt=24:0:0
#$ -cwd
#$ -pe *_fast 1
#$ -notify

trap "" TERM

set -o pipefail