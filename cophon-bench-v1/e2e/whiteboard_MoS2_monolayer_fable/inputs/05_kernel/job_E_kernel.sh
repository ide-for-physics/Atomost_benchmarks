#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -t 00:28:00
#SBATCH -J mos2_E_kernel
#SBATCH -o slurm-%j.out
# usage: sbatch job_E_kernel.sh 48 96 144 192   (runs the kernel for each fine mesh in k<N>/, sequentially)
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
NT=${SLURM_NTASKS}
cd $SLURM_SUBMIT_DIR
for n in "$@"; do
  cd $SLURM_SUBMIT_DIR/k$n
  echo "START k$n $(date -Is)"
  srun -n $NT $BIN/epw.x -npool $NT -in epw_k$n.in > epw_k$n.out
  echo "END   k$n $(date -Is)  $(grep -c . Gamma_alphabeta_s.dat 2>/dev/null) lines"
  cp Gamma_alphabeta_s.dat Gamma_alphabeta_s_${n}x${n}x1.dat 2>/dev/null
done
