#!/bin/bash
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00
#SBATCH --job-name=gap_bands2
module load LUMI partition/C
module load PrgEnv-gnu
module load cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd $SLURM_SUBMIT_DIR
srun -n 32 $BIN/pw.x -nk 4 -in scf_b.in > scf_b.out
srun -n 32 $BIN/pw.x -nk 4 -in bands_b.in > bands_b.out
cd $SLURM_SUBMIT_DIR/wan_bands
srun -n 32 $BIN/pw2wannier90.x -nk 32 -in ../p2w_eig.in > p2w_eig.out
srun -n 1 $BIN/wannier90.x gap > wannier_bands.stdout
echo JOB_DONE $(date -Is)
