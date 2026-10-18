#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --mem=200G
#SBATCH --job-name=gap_epw1
#SBATCH --output=job4_%j.log
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/04_epw
srun -n 128 $BIN/epw.x -nk 128 -in epw1.in > epw1.out || { echo J4_FAILED $(date -Is); exit 1; }
echo J4_DONE $(date -Is)
