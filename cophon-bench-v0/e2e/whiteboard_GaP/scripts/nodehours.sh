#!/bin/bash
# usage: nodehours.sh jobid ...  -> prints elapsed, cpus, node-hours = NCPUS*elapsed/128 (shared) or NNodes*elapsed (exclusive)
for j in "$@"; do
  sacct -j $j -n -P --format=JobID,JobName,Partition,State,Elapsed,NCPUS,NNodes | grep -v "\.batch\|\.extern\|\.[0-9]" | awk -F'|' '{
    split($5,t,":"); h=t[1]+t[2]/60+t[3]/3600; nh=($3=="standard")? $7*h : $6*h/128;
    printf "%s | %s | %s | %s | elapsed %s | cpus %s | nodes %s | node-hours %.4f\n",$1,$2,$3,$4,$5,$6,$7,nh}'
done
