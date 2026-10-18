#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --job-name=gap_ph_nscf
# DFPT (4x4x4 q, Gamma included) then 8x8x8 NSCF with 20 bands, in one allocation.
# ph.x reads the SCF save data before the NSCF overwrites it.
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
srun -n 32 $BIN/ph.x -nk 4 -in ph.in > ph.out
srun -n 32 $BIN/pw.x -nk 4 -in nscf.in > nscf.out
echo JOB_DONE $(date -Is)
