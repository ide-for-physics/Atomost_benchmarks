#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --job-name=mos2_H
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer
export PATH=$T/bin:$PATH
for N in 72 96 120; do
  d=$R/05_epw/A2_k${N}; mkdir -p $d; cp $R/05_epw/epw_A2_k${N}.in $d/epw.in; cd $d
  srun -n 32 $T/EPW/bin/epw.x -nk 32 -i epw.in > epw.out 2>&1; echo "epw A2 k${N} rc $?"
done
