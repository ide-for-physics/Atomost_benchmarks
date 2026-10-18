#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=08:00:00
#SBATCH --job-name=b2o2se_chain
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
# SCF -> NSCF (explicit 8x8x8 list) -> ph.x at Gamma (EPW-style dvscf) -> pp.py gather. Same order as EPW test-suite.
set -e
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
cd "$ROOT/run"
srun -n 32 $T/bin/pw.x -npool 8 -in scf.in > scf.out
srun -n 32 $T/bin/pw.x -npool 8 -in nscf.in > nscf.out
srun -n 32 $T/bin/ph.x -npool 8 -in ph.in > ph.out
python3 $T/EPW/bin/pp.py < pp.in > pp.out
echo CHAIN_DONE
