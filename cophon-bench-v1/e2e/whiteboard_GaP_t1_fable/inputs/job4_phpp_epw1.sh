#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=gap_epw1
#SBATCH --output=job4_%j.log
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/02_ph
bash gather_save.sh > gather_save.log 2>&1
srun -n 1 $BIN/q2r.x -in q2r.in > q2r.out
srun -n 1 $BIN/matdyn.x -in matdyn.in > matdyn.out
srun -n 1 $BIN/dynmat.x -in dynmat.in > dynmat.out
srun -n 1 $BIN/dynmat.x -in dynmat_q001.in > dynmat_q001.out
cd $SLURM_SUBMIT_DIR/04_epw
srun -n 64 $BIN/epw.x -nk 64 -in epw1.in > epw1.out
echo J4_DONE $(date -Is)
