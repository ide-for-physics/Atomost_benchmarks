#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=04:00:00
#SBATCH --job-name=b2o2se_wv
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
# Wannier variant: prep (wannierize + epwwrite) then band-plot check, in $ROOT/$DIR
set -e
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
cd "$ROOT/$DIR"
srun -n 32 $T/bin/epw.x -npool 32 -in "$PREP" > "$PREP.out"
srun -n 32 $T/bin/epw.x -npool 32 -in "$BAND" > "$BAND.out"
echo WV_DONE
