#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=03:00:00
#SBATCH --job-name=mos2_G
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer
export PATH=$T/bin:$PATH
for name in A2 B2; do
  d=$R/05_epw/${name}_k48; mkdir -p $d; cp $R/05_epw/epw_${name}_k48.in $d/epw.in; cd $d
  srun -n 32 $T/EPW/bin/epw.x -nk 32 -i epw.in > epw.out 2>&1; echo "epw ${name}48 rc $?"
done
