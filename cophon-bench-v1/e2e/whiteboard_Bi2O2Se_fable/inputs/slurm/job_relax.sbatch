#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH -c 1
#SBATCH -t 00:25:00
#SBATCH -J bos_relax
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun -n 64 $BIN/pw.x -nk 16 -in relax.in > relax.out
echo "END $(date -Is)"
