#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=48
#SBATCH --cpus-per-task=1
#SBATCH -t 00:28:00
#SBATCH -J mos2_F_epw_scdm20
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
# own outdir so that the stage-1 mos2.epmatwp in ../03_nscf/tmp is not overwritten
if [ ! -d ../03_nscf/tmp_scdm/mos2.save ]; then mkdir -p ../03_nscf/tmp_scdm && cp -r ../03_nscf/tmp/mos2.save ../03_nscf/tmp_scdm/; fi
srun -n 48 $BIN/epw.x -npool 48 -in epw1_scdm20.in > epw1_scdm20.out
echo "END $(date -Is)"
