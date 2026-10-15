#!/bin/bash
#SBATCH --job-name=nbfesb_ph
#SBATCH --account=project_<id>
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --time=01:30:00
#SBATCH --output=slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun $BIN/ph.x -nk 8 -in ph.in > ph.out || { echo PH_FAILED; exit 1; }
grep -q "JOB DONE" ph.out || { echo PH_NOT_DONE; exit 1; }
echo "ph done $(date -Is)"
srun -n 1 $BIN/dynmat.x -in dynmat.in > dynmat.out
srun -n 1 $BIN/dynmat.x -in dynmat_LO.in > dynmat_LO.out
# EPW save directory (pp.py is interactive: it asks for the prefix)
module load cray-python 2>/dev/null
echo nbfesb | python3 $BIN/pp.py > pp.out 2>&1
ls -la save/ >> pp.out
echo "END $(date -Is)"
