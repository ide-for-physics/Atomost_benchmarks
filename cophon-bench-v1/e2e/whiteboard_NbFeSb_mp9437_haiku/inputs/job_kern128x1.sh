#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=240G
#SBATCH --exclusive
#SBATCH --cpus-per-task=1
#SBATCH --time=08:00:00
#SBATCH --job-name=nbfesb_kern
module load LUMI partition/C PrgEnv-gnu cray-fftw
TC=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/NbFeSb_mp9437
cd $R/run
# NKF is set by the submitter: input epw_kern${NKF}.in, output copied to kernel_nkf${NKF}/
srun -n 128 $TC/bin/epw.x -npool 128 -in epw_kern${NKF}.in > epw_kern${NKF}.out 2>&1
mkdir -p kernel_nkf${NKF} && mv Gamma_alphabeta_s.dat kernel_nkf${NKF}/ 2>/dev/null
