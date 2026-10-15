#!/bin/bash
#SBATCH --job-name=gap_elph_G16
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1750M
#SBATCH --time=00:40:00
#SBATCH --output=job_epw_elph_G16.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP/wan16_G_s10
echo "START $(date -Is)"
srun --cpu-bind=cores $BIN/epw.x -nk 128 -in epw_elph_G16.in > epw_elph_G16.out
echo "END $(date -Is)"
