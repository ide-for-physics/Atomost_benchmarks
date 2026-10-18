#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=08:00:00
#SBATCH --job-name=b2o2se_ph
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
# DFPT at Gamma from a fresh SCF on the 8x8x8 grid (IBZ). The NSCF full-grid list must NOT be used by ph.x (16x cost).
set -e
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
cd "$ROOT/phrun"
srun -n 32 $T/bin/pw.x -npool 8 -in scf.in > scf.out
srun -n 32 $T/bin/ph.x -npool 8 -in ph.in > ph.out
python3 $T/EPW/bin/pp.py < pp.in > pp.out
rm -rf "$ROOT/run/save"; cp -r save "$ROOT/run/save"
echo PH_DONE
