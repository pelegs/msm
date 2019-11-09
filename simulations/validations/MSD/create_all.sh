#!/usr/bin/env bash

rm data/MSD_all.data
cat data/*.data | sort -n > data/MSD_all.data
