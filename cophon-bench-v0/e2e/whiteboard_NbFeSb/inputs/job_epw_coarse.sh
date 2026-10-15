#!/bin/bash
#SBATCH --job-name=nbfesb_epwc
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
for d in wanA16 wanB19 wanC22; do
  cd $SLURM_SUBMIT_DIR/$d
  echo "=== $d start $(date -Is)"
  srun -n 128 $BIN/epw.x -nk 128 -in epw_coarse.in > epw_coarse.out 2> epw_coarse.err
  echo "=== $d rc=$? end $(date -Is)"; grep -i "error\|Error" epw_coarse.out | head -3
  ls -la band.eig nbfesb.wout nbfesb.epmatwp epwdata.fmt 2>/dev/null
done
echo "END $(date -Is)"
