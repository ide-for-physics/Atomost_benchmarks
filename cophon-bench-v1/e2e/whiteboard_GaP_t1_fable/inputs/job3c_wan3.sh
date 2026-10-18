#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:30:00
#SBATCH --job-name=gap_wan3
#SBATCH --output=job3c_%j.log
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/03_wan
for S in E F G; do
  rm -f gap$S.wout gap$S.werr
  srun -n 1 $BIN/wannier90.x -pp gap$S
  srun -n 32 $BIN/pw2wannier90.x -in pw2wan_$S.in > pw2wan_$S.out
done
for S in E F G; do
  srun -n 1 --exact --overlap $BIN/wannier90.x gap$S &
done
wait
rm -f gapE.amn gapE.mmn gapE.chk gapF.amn gapF.mmn gapF.chk gapG.amn gapG.mmn gapG.chk
echo J3C_DONE $(date -Is)
