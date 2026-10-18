#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=%x_%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/KNbO3_mp7375/nscf
srun -n 1 $T/wannier90.x knbo3 > knbo3_w90.out 2>&1; echo W90_RC $?
