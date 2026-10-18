#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -J kno_nscf
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=120G
#SBATCH -t 00:20:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
BIN=$T/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun $BIN/pw.x -nk 8 -in scf.in > scf.out
echo "SCF done $(date -Is)"
srun $BIN/pw.x -nk 8 -in nscf.in > nscf.out
echo "END $(date -Is)"
