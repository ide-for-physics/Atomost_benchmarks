#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH -c 1
#SBATCH -t 00:15:00
#SBATCH -J bos_kern24
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
for f in crystal.fmt epwdata.fmt vmedata.fmt dmedata.fmt wigner.fmt bos.ukk; do ln -sf ../epw/$f .; done
cp ../epw/qgamma.txt . 2>/dev/null
srun -n 128 $BIN/epw.x -npool 128 -in epw_kern24.in > epw_kern24.out
echo "EPW exit $? $(date -Is)"
ls -la Gamma_alphabeta_s.dat 2>/dev/null
echo "END $(date -Is)"
