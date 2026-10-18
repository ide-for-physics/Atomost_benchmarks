#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -J cds_relax
#SBATCH -N 1
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --mem=100G
#SBATCH -t 00:15:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672/scf
date
srun $T/pw.x -nk 4 -in relax.in > relax.out
date
