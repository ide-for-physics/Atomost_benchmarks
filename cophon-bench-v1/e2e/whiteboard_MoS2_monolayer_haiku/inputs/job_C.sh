#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=06:00:00
#SBATCH --job-name=mos2_C
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer
export PATH=$T/bin:$PATH
cd $R/04_bands
srun -n 32 pw.x -nk 4 -i scf.in > scf.out 2>&1; echo "bands-scf rc $?"
srun -n 32 pw.x -nk 4 -i bands.in > bands.out 2>&1; echo "bands rc $?"
for name in A B; do for N in 48 72 96; do
  d=$R/05_epw/${name}_k${N}; mkdir -p $d; cp $R/05_epw/epw_${name}_k${N}.in $d/epw.in; cd $d
  srun -n 32 epw.x -nk 32 -i epw.in > epw.out 2>&1; echo "epw ${name}${N} rc $?"
done; done
