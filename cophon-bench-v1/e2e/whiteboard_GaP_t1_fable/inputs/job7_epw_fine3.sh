#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=4
#SBATCH --ntasks=512
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --mem=200G
#SBATCH --job-name=gap_epwk
#SBATCH --output=job5_%j.log
# usage: sbatch job5_epw_fine.sh "48 72 96"   (fine k-meshes, run sequentially; q-mesh is Gamma only)
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
MESHES=${1:-"48 72 96"}
cd $SLURM_SUBMIT_DIR/04_epw
for NKF in $MESHES; do
  sed "s/__NKF__/$NKF/g" epw2_template.in > epw2_k$NKF.in
  rm -f Gamma_alphabeta_s.dat Pi_0.dat
  srun -n 512 $BIN/epw.x -nk 512 -in epw2_k$NKF.in > epw2_k$NKF.out || { echo J5_FAILED $NKF $(date -Is); exit 1; }
  mkdir -p k$NKF
  mv Gamma_alphabeta_s.dat k$NKF/Gamma_alphabeta_s.dat 2>/dev/null
  mv Pi_0.dat k$NKF/Pi_0.dat 2>/dev/null
  cp epw2_k$NKF.in epw2_k$NKF.out k$NKF/
  echo J5_MESH_DONE $NKF $(date -Is)
done
echo J5_DONE $(date -Is)
