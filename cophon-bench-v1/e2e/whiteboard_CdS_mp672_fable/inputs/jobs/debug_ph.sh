#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -J cds_ph
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --mem=200G
#SBATCH -t 00:25:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672/calc
cd $R/ph
date; echo "== ph"
srun $T/bin/ph.x -nk 8 -in ph.in > ph.out
date; echo "== dynmat"
srun -n 1 $T/bin/dynmat.x -in dynmat.in > dynmat.out
echo cds | python3 $T/EPW/bin/pp.py > pp.log 2>&1
ls -la save
date
