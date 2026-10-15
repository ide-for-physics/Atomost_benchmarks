#!/bin/bash
#SBATCH --job-name=gap_wC_s9
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1750M
#SBATCH --time=01:30:00
#SBATCH --output=job_wan_C_s9.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP
D=$ROOT/wan_C_s9; mkdir -p $D; cd $D
ln -sfn $ROOT/run/gap.save gap.save; ln -sfn $ROOT/run/save save
echo "START $(date -Is)"
srun --cpu-bind=cores $BIN/epw.x -nk 16 -in epw_wan_C_s9.in > epw_wan_C_s9.out
echo "END $(date -Is)"
