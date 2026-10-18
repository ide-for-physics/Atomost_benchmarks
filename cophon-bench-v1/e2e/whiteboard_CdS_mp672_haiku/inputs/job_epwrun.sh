#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --time=03:00:00
#SBATCH --job-name=cds_epwk
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
cd $R/$RUNDIR
srun --ntasks=64 $BIN/epw.x -npool 64 -in epw.in > epw.out 2> epw.err
echo "EPW_RC $?"
