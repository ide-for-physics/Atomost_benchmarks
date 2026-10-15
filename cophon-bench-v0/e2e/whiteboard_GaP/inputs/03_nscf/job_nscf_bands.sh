#!/bin/bash
#SBATCH --job-name=gap_nscf
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1750M
#SBATCH --time=01:30:00
#SBATCH --output=job_nscf_bands.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP
echo "START $(date -Is)"
cd $ROOT/run_bands
srun --cpu-bind=cores $BIN/pw.x -nk 32 -in bands.in > bands.out
echo "BANDS_DONE $(date -Is)"
cd $ROOT/run
srun --cpu-bind=cores $BIN/pw.x -nk 32 -in nscf.in > nscf.out
echo "NSCF_DONE $(date -Is)"
