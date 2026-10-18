#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --job-name=nbfesb_kern12
module load LUMI partition/C PrgEnv-gnu cray-fftw
TC=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/NbFeSb_mp9437
cd $R/run
srun -n 32 $TC/bin/epw.x -npool 32 -in epw_kern12.in > epw_kern12.out 2>&1
