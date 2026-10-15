#!/bin/bash
#SBATCH --job-name=epwk64ad
#SBATCH --account=project_<id>
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/fine_k64_adsmear
echo "START $(date -Is)"
NP=$((SLURM_NNODES*128))
srun -n $NP $BIN/epw.x -nk $NP -in epw_fine.in > epw_fine.out || { echo EPW_FAILED; exit 1; }
echo "END $(date -Is)"
