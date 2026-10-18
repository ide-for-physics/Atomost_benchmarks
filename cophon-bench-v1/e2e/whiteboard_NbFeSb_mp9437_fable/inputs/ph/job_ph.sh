#!/bin/bash
#SBATCH --job-name=nfs_ph
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=120G
#SBATCH --time=03:00:00
#SBATCH --output=ph.slurm.out
source ../env.sh
srun ph.x -nk 8 -in ph.in > ph.out
