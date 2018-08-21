#!/usr/bin/env bash

from=$1
to=$2

cp simulation/"$from.py" simulation/"$to.py"
cp data/"$from.data" data/"$to.data"
cp gp/"$from.gp" gp/"$to.gp"
