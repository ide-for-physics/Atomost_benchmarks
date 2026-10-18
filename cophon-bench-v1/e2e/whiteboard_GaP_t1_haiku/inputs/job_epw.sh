#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=03:00:00
#SBATCH --job-name=gap_epw
# usage (from the run dir): sbatch job_epw.sh <input> <output>
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
srun -n 32 $BIN/epw.x -nk 32 -in $1 > $2
echo JOB_DONE $(date -Is)
