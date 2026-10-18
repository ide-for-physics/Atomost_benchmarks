#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH -t 00:20:00
#SBATCH -J sns2_epw_band
#SBATCH -o slurm-%j.out
# stage 2: post-process DFPT into save/ (EPW layout, as EPW/examples/diamond/phonons/pp.py), then Wannierize + band plot
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd "$SLURM_SUBMIT_DIR/epw"
srun -n 64 $BIN/epw.x -npool 64 -in epw_band.in > epw_band.out
echo EPW_BAND_DONE $(date -Is)
