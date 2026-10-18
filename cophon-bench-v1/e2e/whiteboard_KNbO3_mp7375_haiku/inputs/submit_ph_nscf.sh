#!/bin/bash
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/KNbO3_mp7375
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $R/ph && J1=$(sbatch --job-name=knbo_ph --export=ALL,WD=$R/ph,BIN=$T/ph.x,ARGS='-nk 4 -in ph.in' $R/job_run.sbatch | awk '{print $4}')
cd $R/nscf && J2=$(sbatch --job-name=knbo_nscf --export=ALL,WD=$R/nscf,BIN=$T/pw.x,ARGS='-nk 4 -in nscf.in' $R/job_run.sbatch | awk '{print $4}')
echo "PH=$J1 NSCF=$J2"
