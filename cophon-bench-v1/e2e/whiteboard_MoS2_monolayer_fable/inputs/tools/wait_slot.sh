#!/bin/bash
# wait_slot.sh JOBID : poll every 120 s until a debug slot is free (fewer than 2 of my debug jobs)
# or until job JOBID is no longer PENDING. Prints the state and exits.
J=$1
while true; do
  d=$(squeue -u $USER -p debug -h | wc -l)
  s=$(squeue -j $J -h -o %T 2>/dev/null)
  if [ "$d" -lt 2 ] || [ "$s" != "PENDING" ]; then
    echo "debugjobs=$d job_$J=$s $(date -Is)"
    exit 0
  fi
  sleep 120
done
