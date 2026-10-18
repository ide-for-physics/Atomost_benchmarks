#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:20:00
#SBATCH --job-name=cds_wanb
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
module load LUMI partition/C PrgEnv-gnu cray-fftw
cd $R/wan_bands
srun --ntasks=1 $BIN/wannier90.x cds > wanbands.stdout 2>&1
echo "W90_RC $?"
