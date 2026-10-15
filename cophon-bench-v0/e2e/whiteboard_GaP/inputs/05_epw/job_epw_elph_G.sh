#!/bin/bash
#SBATCH --job-name=gap_elph_G
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1750M
#SBATCH --time=00:40:00
#SBATCH --output=job_epw_elph_G.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP/wan_G_s10
echo "START $(date -Is)"
srun --cpu-bind=cores $BIN/epw.x -nk 64 -in epw_elph_G.in > epw_elph_G.out
echo "END $(date -Is)"
