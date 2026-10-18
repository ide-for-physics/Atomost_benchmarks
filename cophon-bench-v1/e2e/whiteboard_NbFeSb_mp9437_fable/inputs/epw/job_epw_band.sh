#!/bin/bash
#SBATCH --job-name=nfs_epwband
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=60G
#SBATCH --time=01:00:00
#SBATCH --output=epw_band.slurm.out
source ../env.sh
srun epw.x -nk 2 -in epw_band.in > epw_band.out
