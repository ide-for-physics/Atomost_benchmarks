#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=debug
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=cds_nscf
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
cd $R/nscf
srun --ntasks=32 $BIN/pw.x -nk 32 -in nscf_coarse.in > nscf_coarse.out 2> nscf_coarse.err
echo "NSCF_RC $?"
