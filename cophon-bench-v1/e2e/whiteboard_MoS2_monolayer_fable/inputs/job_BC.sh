#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -t 00:28:00
#SBATCH -J mos2_BC_ph_nscf
#SBATCH -o slurm-%j.out
# Runs the Gamma-point DFPT (02_ph/job_B.sh) and then the band path + NSCF grid (03_nscf/job_C.sh) in one short debug job.
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer/fable_run
bash 02_ph/job_B.sh
bash 03_nscf/job_C.sh
