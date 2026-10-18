#!/bin/bash
#SBATCH --job-name=nfs_bands
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=60G
#SBATCH --time=01:00:00
#SBATCH --output=bands.slurm.out
source ../env.sh
srun pw.x -nk 8 -in bands.in > bands.out
