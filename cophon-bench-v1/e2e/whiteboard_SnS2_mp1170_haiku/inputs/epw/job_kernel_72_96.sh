#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p small
#SBATCH -N 1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH -t 02:00:00
#SBATCH -J sns2_kern7296
#SBATCH -o slurm-%j.out
# convergence meshes 72^3 then 96^3 in one allocation (same photon grid 0.1..6.02 eV, step 0.02 eV)
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd "$SLURM_SUBMIT_DIR/epw"
for MESH in 72 96; do
  srun -n 128 $BIN/epw.x -npool 128 -in epw_kernel_k${MESH}.in > epw_kernel_k${MESH}.out
  cp Gamma_alphabeta_s.dat Gamma_alphabeta_s_k${MESH}.dat
  echo KERNEL_DONE_${MESH} $(date -Is)
done
