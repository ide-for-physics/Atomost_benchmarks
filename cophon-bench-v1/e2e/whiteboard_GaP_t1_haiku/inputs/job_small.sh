#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=gap
# usage: sbatch job_small.sh <binary> <input> <output> [extra flags]
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
BIN_NAME=$1; IN=$2; OUT=$3; shift 3
srun -n 32 $BIN/$BIN_NAME $* -in $IN > $OUT
