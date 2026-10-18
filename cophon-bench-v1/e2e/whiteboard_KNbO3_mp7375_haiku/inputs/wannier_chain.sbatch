#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --output=%x_%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/KNbO3_mp7375/nscf
$T/wannier90.x -pp knbo3 > knbo3_pp.out 2>&1; echo PP_RC $?
srun -n 32 $T/pw2wannier90.x -in pw2wan.in > pw2wan.out 2>&1; echo PW2WAN_RC $?
srun -n 1 $T/wannier90.x knbo3 > knbo3_w90.out 2>&1; echo W90_RC $?
