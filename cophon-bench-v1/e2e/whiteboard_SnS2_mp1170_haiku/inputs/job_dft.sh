#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH -t 00:20:00
#SBATCH -J sns2_dft
#SBATCH -o slurm-%j.out
# stage 1: SCF (sealed cell, 12x12x6) -> DFPT at Gamma (+ASR) -> NSCF full grid (nbnd 30) -> bands on the path
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd "$SLURM_SUBMIT_DIR"
srun -n 64 $BIN/pw.x -nk 8 -in scf.in > scf.out || exit 1
srun -n 64 $BIN/ph.x -nk 8 -in ph.in > ph.out || exit 1
srun -n 1 $BIN/dynmat.x -in dynmat.in > dynmat.log
srun -n 64 $BIN/pw.x -nk 16 -in nscf.in > nscf.out || exit 1
cp -r tmp tmp_bands
srun -n 64 $BIN/pw.x -nk 8 -in bands.in > bands.out || exit 1
srun -n 1 $BIN/bands.x -in bandsx.in > bandsx.out
rm -rf tmp_bands
echo DFT_STAGE_DONE $(date -Is)
