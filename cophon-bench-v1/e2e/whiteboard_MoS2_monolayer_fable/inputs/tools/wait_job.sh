#!/bin/bash
# wait_job.sh JOBID : poll every 120 s until job JOBID has left the queue (or failed); print sacct summary.
J=$1
while squeue -j $J -h 2>/dev/null | grep -q . ; do
  sleep 120
done
sacct -j $J --format=JobID,JobName%30,Partition,State,Elapsed,NNodes,NCPUS,ExitCode -P | head -3
date -Is
