#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH -c 1
#SBATCH -t 00:20:00
#SBATCH -J bos_nscf
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun -n 128 $BIN/pw.x -nk 32 -in nscf.in > nscf.out || exit 1
echo "NSCF done $(date -Is)"
echo "END $(date -Is)"
