#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -J kno_bands
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=60G
#SBATCH -t 00:15:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
BIN=$T/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun $BIN/pw.x -nk 4 -in scf.in > scf.out
echo "SCF done $(date -Is)"
srun $BIN/pw.x -nk 4 -in bands.in > bands.out
echo "BANDS done $(date -Is)"
srun $BIN/projwfc.x -nk 4 -in projwfc.in > projwfc.out
echo "END $(date -Is)"
rm -rf tmp/kno.save/wfc*.dat
