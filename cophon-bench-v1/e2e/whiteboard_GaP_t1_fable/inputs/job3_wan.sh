#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=gap_wan
#SBATCH --output=job3_%j.log
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/03_wan
for S in B C; do
  srun -n 1 $BIN/wannier90.x -pp gap$S
  srun -n 32 $BIN/pw2wannier90.x -in pw2wan_$S.in > pw2wan_$S.out
  srun -n 1 $BIN/wannier90.x gap$S
done
# DFT bands at exactly the Wannier90 band-path k-points (same for B and C)
N=$(head -1 gapB_band.kpt | awk '{print $1}')
cp bands_wk_template.in bands_wk.in
echo "K_POINTS crystal" >> bands_wk.in
echo "$N" >> bands_wk.in
tail -n +2 gapB_band.kpt >> bands_wk.in
srun -n 32 $BIN/pw.x -nk 4 -in bands_wk.in > bands_wk.out
echo J3_DONE $(date -Is)
