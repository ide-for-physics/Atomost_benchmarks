#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=03:00:00
#SBATCH --job-name=gap_nscf_epw
# full-grid (no symmetry) 8x8x8 NSCF, then EPW 48^3 in the same allocation.
# usage (from haiku_run): sbatch job_nscf_epw.sh
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd $SLURM_SUBMIT_DIR
srun -n 32 $BIN/pw.x -nk 32 -in nscf_full8.in > nscf_full8.out
cd $SLURM_SUBMIT_DIR/epw48
srun -n 32 $BIN/epw.x -nk 32 -in epw_k48.in > epw_k48.out
echo JOB_DONE $(date -Is)
