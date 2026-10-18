#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:30:00
#SBATCH --job-name=gap_wan2
#SBATCH --output=job3b_%j.log
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/03_wan
# redo NSCF (the band run in J3 overwrote the wavefunctions in tmp/)
srun -n 32 $BIN/pw.x -nk 8 -in nscf.in > nscf.out
for S in D E F G; do
  srun -n 1 $BIN/wannier90.x -pp gap$S
  srun -n 32 $BIN/pw2wannier90.x -in pw2wan_$S.in > pw2wan_$S.out
  srun -n 1 $BIN/wannier90.x gap$S
  rm -f gap$S.amn gap$S.mmn gap$S.chk
done
echo J3B_DONE $(date -Is)
