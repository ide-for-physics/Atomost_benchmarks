#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH -c 1
#SBATCH -t 00:12:00
#SBATCH -J bos_ph_a
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun -n 128 $BIN/ph.x -nk 32 -in ph_a.in > ph_a.out
echo "PH-A exit $? $(date -Is)"
grep -c "Maximum CPU time exceeded" ph_a.out
echo "END $(date -Is)"
