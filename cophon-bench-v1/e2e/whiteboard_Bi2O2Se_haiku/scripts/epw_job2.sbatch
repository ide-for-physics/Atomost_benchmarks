#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=12:00:00
#SBATCH --job-name=b2o2se_kern
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
# usage: sbatch --export=ALL,ROOT=...,DIR=kern48,IN=epw_kern48.in,OUT=epw_kern48.out epw_job2.sbatch
set -e
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
cd "$ROOT/$DIR"
if [ -n "$SYNC" ]; then cp "$ROOT/run/"*.fmt "$ROOT/run/decay."* "$ROOT/run/bi2o2se.ukk" "$ROOT/run/bi2o2se_hr.dat" "$ROOT/run/bi2o2se_wsvec.dat" "$ROOT/run/epwdata.fmt" .; fi
srun -n 32 $T/bin/epw.x -npool 32 -in "$IN" > "$OUT"
echo EPW_DONE
