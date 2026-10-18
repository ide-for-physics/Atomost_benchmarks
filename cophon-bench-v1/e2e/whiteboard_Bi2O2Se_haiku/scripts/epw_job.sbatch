#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=06:00:00
#SBATCH --job-name=b2o2se_epw
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
# usage: sbatch --export=ALL,ROOT=...,IN=epw_wan.in,OUT=epw_wan.out epw_job.sbatch   (runs in $ROOT/run)
set -e
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
cd "$ROOT/run"
srun -n 32 $T/bin/epw.x -npool 32 -in "$IN" > "$OUT"
echo EPW_DONE
