#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --job-name=nbfesb_nscf8
module load LUMI partition/C PrgEnv-gnu cray-fftw
TC=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/NbFeSb_mp9437
cd $R/run
mkdir -p k8/nbfesb.save && cp tmp/nbfesb.save/charge-density.dat tmp/nbfesb.save/data-file-schema.xml tmp/nbfesb.save/*.upf k8/nbfesb.save/
srun -n 32 $TC/bin/pw.x -nk 16 -in nscf_k8.in > nscf_k8.out 2>&1
