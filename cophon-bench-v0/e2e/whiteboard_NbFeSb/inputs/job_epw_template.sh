#!/bin/bash
#SBATCH --job-name=__NAME__
#SBATCH --account=project_<id>
#SBATCH --partition=standard
#SBATCH --nodes=__NODES__
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --time=__TIME__
#SBATCH --output=slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/__DIR__
echo "START $(date -Is)"
NP=$((SLURM_NNODES*128))
srun -n $NP $BIN/epw.x -nk $NP -in __INPUT__ > __OUTPUT__ || { echo EPW_FAILED; exit 1; }
echo "END $(date -Is)"
