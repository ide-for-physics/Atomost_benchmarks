#!/bin/bash
#SBATCH --job-name=gap_k168
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=128
#SBATCH --mem-per-cpu=1750M
#SBATCH --cpus-per-task=1
#SBATCH --time=03:00:00
#SBATCH --output=job_epw_k168.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP
SRC=$ROOT/wan16_G_s10
D=$ROOT/k168
mkdir -p $D && cd $D
# the kernel runs restart from the Wannier-representation data of the wannierization run (run/): link, do not copy
for f in gap.epmatwp epwdata.fmt crystal.fmt vmedata.fmt dmedata.fmt gap.kgmap gap.kmap gap.mmn gap.bvec; do [ -e $SRC/$f ] && ln -sf $SRC/$f . ; done
ln -sf $SRC/gap.ukk gap.ukk
ln -sfn $SRC/save save
ln -sfn $SRC/gap.save gap.save
echo "START $(date -Is)"
NP=128
srun --cpu-bind=cores $BIN/epw.x -nk $NP -in epw_k168.in > epw_k168.out
echo "END $(date -Is)"
