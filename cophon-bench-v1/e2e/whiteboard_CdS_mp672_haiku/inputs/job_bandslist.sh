#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --job-name=cds_bl
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
cd $R/bands
srun --ntasks=64 $BIN/pw.x -nk 16 -in bands_list.in > bands_list.out 2> bands_list.err
echo "PW_RC $?"
