#!/bin/bash
#SBATCH --job-name=nfs_nscf
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=120G
#SBATCH --time=02:00:00
#SBATCH --output=nscf.slurm.out
source ../env.sh
srun pw.x -nk 16 -in nscf.in > nscf.out
