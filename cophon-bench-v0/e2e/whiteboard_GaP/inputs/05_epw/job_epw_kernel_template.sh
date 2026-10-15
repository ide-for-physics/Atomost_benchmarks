#!/bin/bash
#SBATCH --job-name=gap_kNKF
#SBATCH --account=project_<id>
#SBATCH --partition=PARTITION
#SBATCH --nodes=NNODES
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --time=WALLTIME
#SBATCH --output=job_epw_kNKF.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP
SRC=$ROOT/SRCDIR
D=$ROOT/kNKF
mkdir -p $D && cd $D
# the kernel runs restart from the Wannier-representation data of the wannierization run (run/): link, do not copy
for f in gap.epmatwp epwdata.fmt crystal.fmt vmedata.fmt dmedata.fmt gap.kgmap gap.kmap gap.mmn gap.bvec; do [ -e $SRC/$f ] && ln -sf $SRC/$f . ; done
ln -sf $SRC/gap.ukk gap.ukk
ln -sfn $SRC/save save
ln -sfn $SRC/gap.save gap.save
echo "START $(date -Is)"
NP=$((NNODES*128))
srun --cpu-bind=cores $BIN/epw.x -nk $NP -in epw_kNKF.in > epw_kNKF.out
echo "END $(date -Is)"
