#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=06:00:00
#SBATCH --job-name=mos2_D
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer
export PATH=$T/bin:$PATH
for name in A B; do for N in 48 72 96; do
  d=$R/05_epw/${name}_k${N}; mkdir -p $d; cp $R/05_epw/epw_${name}_k${N}.in $d/epw.in; cd $d
  srun -n 32 $T/EPW/bin/epw.x -nk 32 -i epw.in > epw.out 2>&1; echo "epw ${name}${N} rc $?"
done; done
