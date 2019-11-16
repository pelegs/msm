#!/bin/bash

source /etc/profile.d/modules.sh
module load shared

#$ -S /bin/bash
#$ -N OU_rmsd
#$ -l h_rt=24:0:0
#$ -cwd
#$ -pe *_fast 1
#$ -notify
#$ -t 1-200:1

#$ -o out
#$ -e out

trap "" TERM

set -o pipefail

./rmsd.py $SGE_TASK_ID $1 $2 $3 $4
