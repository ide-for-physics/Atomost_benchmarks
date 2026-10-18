#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --job-name=gap_pipe
# SCF (refresh save) -> ph.x 4x4x4 with fildvscf (for EPW) -> full-grid NSCF 8x8x8 (nbnd 20).
# Run from haiku_run/. EPW is submitted separately afterwards.
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
srun -n 32 $BIN/pw.x -nk 4 -in scf.in > scf.out
srun -n 32 $BIN/ph.x -nk 4 -in ph.in > ph.out
srun -n 32 $BIN/pw.x -nk 32 -in nscf_full8.in > nscf_full8.out
echo JOB_DONE $(date -Is)
