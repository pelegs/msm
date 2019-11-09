#!/bin/bash

source /etc/profile.d/modules.sh
module load shared

#$ -S /bin/bash
#$ -N equib_par
#$ -l h_rt=24:0:0
#$ -cwd
#$ -pe *_fast 1
#$ -notify
#$ -t 1-100:1

#$ -o /home/psapir/tests/test.out
#$ -e /home/psapir/tests/test.err

trap "" TERM

set -o pipefail

./equib.py $1 $SGE_TASK_ID $2 $3 $4 $5
