#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p small
#SBATCH -J cds_epw96
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --mem=0
#SBATCH -t 08:30:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672/calc
cd $R/epw96
date
bash stage96.sh
date
