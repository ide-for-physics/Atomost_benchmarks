#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH -t 00:20:00
#SBATCH -J sns2_kernel
#SBATCH -o slurm-%j.out
# kernel run on a fine k-mesh N (set MESH env at submit: sbatch --export=ALL,MESH=48 job_kernel.sh)
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd "$SLURM_SUBMIT_DIR/epw"
srun -n 64 $BIN/epw.x -npool 64 -in epw_kernel_k${MESH}.in > epw_kernel_k${MESH}.out
cp Gamma_alphabeta_s.dat Gamma_alphabeta_s_k${MESH}.dat
echo KERNEL_DONE_${MESH} $(date -Is)
