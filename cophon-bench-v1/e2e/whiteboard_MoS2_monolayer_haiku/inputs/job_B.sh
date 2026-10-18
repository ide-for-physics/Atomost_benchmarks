#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --job-name=mos2_B
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer
cd $R/02_ph
srun -n 32 $T/bin/ph.x -nk 4 -i ph.in > ph.out 2>&1
echo "ph rc $?"
cd $R/03_nscf
srun -n 32 $T/bin/pw.x -nk 16 -i nscf.in > nscf.out 2>&1
echo "nscf rc $?"
