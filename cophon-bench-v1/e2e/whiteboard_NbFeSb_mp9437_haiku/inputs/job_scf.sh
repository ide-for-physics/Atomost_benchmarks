#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=nbfesb_scf
module load LUMI partition/C PrgEnv-gnu cray-fftw
TC=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/NbFeSb_mp9437
cd $R/run
srun -n 32 $TC/bin/pw.x -nk 4 -in scf.in > scf.out 2>&1
