#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=2
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --job-name=gap_epw2n
# usage (from the run dir): sbatch job_epw_2node.sh <input> <output>; EPW needs npool = ranks
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
srun -n 128 $BIN/epw.x -nk 128 -in $1 > $2
echo JOB_DONE $(date -Is)
