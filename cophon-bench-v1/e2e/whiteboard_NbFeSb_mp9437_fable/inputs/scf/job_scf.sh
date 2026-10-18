#!/bin/bash
#SBATCH --job-name=nfs_scf
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=60G
#SBATCH --time=00:40:00
#SBATCH --output=scf.slurm.out
source ../env.sh
srun pw.x -nk 4 -in scf.in > scf.out
