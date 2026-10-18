#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=gap_j1
#SBATCH --output=job1_%j.log
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR/01_scf
srun -n 32 $BIN/pw.x -nk 4 -in scf_ph.in > scf_ph.out
cd $SLURM_SUBMIT_DIR/03_wan
srun -n 32 $BIN/pw.x -nk 4 -in scf.in > scf.out
srun -n 32 $BIN/pw.x -nk 4 -in bands_path.in > bands_path.out
srun -n 32 $BIN/pw.x -nk 8 -in nscf.in > nscf.out
echo J1_DONE $(date -Is)
