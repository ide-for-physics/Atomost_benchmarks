#!/bin/bash
#SBATCH --job-name=nfs_epwwan
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --time=02:00:00
#SBATCH --output=epw_wan.slurm.out
source ../env.sh
srun epw.x -nk 64 -in epw_wan.in > epw_wan.out
