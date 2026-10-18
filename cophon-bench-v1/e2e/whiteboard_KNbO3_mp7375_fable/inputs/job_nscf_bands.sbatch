#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -J kno_nscf_bands
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=120G
#SBATCH -t 00:25:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
BIN=$T/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/KNbO3_mp7375/fable_v1
echo "START $(date -Is)"
# 1) full-grid NSCF for EPW (8x8x8, 512 k, 50 bands)
cd $ROOT/nscf
srun $BIN/pw.x -nk 8 -in scf.in > scf.out
echo "NSCF/SCF done $(date -Is)"
srun $BIN/pw.x -nk 8 -in nscf.in > nscf.out
echo "NSCF done $(date -Is)"
# 2) DFT bands along the high-symmetry path + projections
cd $ROOT/bands
srun $BIN/pw.x -nk 8 -in scf.in > scf.out
srun $BIN/pw.x -nk 8 -in bands.in > bands.out
echo "BANDS done $(date -Is)"
srun $BIN/projwfc.x -nk 8 -in projwfc.in > projwfc.out
echo "END $(date -Is)"
rm -rf $ROOT/bands/tmp/kno.save/wfc*.dat
