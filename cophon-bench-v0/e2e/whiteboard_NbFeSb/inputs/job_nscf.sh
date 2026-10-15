#!/bin/bash
#SBATCH --job-name=nbfesb_nscf
#SBATCH --account=project_<id>
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --time=01:00:00
#SBATCH --output=slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun $BIN/pw.x -nk 32 -in nscf.in > nscf.out || { echo NSCF_FAILED; exit 1; }
grep -q "JOB DONE" nscf.out || { echo NSCF_NOT_DONE; exit 1; }
echo "END $(date -Is)"
