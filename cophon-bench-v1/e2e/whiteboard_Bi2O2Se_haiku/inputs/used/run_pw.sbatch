#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --job-name=b2o2se_pw
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
# usage: sbatch --export=ALL,ROOT=...,DIR=relax,IN=relax.in,OUT=relax.out run_pw.sbatch
set -e
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd "$ROOT/$DIR"
srun -n "${NTASKS:-64}" $BIN/pw.x -npool "${NPOOL:-8}" -in "$IN" > "$OUT"
