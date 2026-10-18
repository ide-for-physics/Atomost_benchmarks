#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -t 00:28:00
#SBATCH -J mos2_A_relax_scf
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun -n 128 $BIN/pw.x -nk 8 -in relax.in > relax.out
python3 mkscf.py
srun -n 128 $BIN/pw.x -nk 8 -in scf.in > scf.out
echo "END $(date -Is)"
