#!/bin/bash
# usage: wait_job.sh <jobid> <poll_seconds> <max_polls>
# Prints the Slurm state every poll until the job is RUNNING/finished (or gone from the queue).
JOB=$1; P=${2:-600}; N=${3:-11}
for i in $(seq 1 "$N"); do
  st=$(ssh lumi "squeue -j $JOB -h -o '%T %M %S %R'" 2>&1)
  echo "$(date -u '+%Y-%m-%d %H:%M UTC') [$JOB] ${st:-<not in queue>}"
  case "$st" in
    PENDING*) sleep "$P";;
    *) break;;
  esac
done
