#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH -t 00:20:00
#SBATCH -J sns2_epw_wan
#SBATCH -o slurm-%j.out
# stage 2: post-process DFPT into save/ (EPW layout, as EPW/examples/diamond/phonons/pp.py), then Wannierize + band plot
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
export PATH=$BIN:$PATH
cd "$SLURM_SUBMIT_DIR"
rm -rf save && mkdir -p save
cp sns2.dyn1 save/sns2.dyn_q1
cp tmp/_ph0/sns2.dvscf1 save/sns2.dvscf_q1
cp -r tmp/_ph0/sns2.phsave save/
cd epw
srun -n 64 $BIN/epw.x -npool 64 -in epw_wan.in > epw_wan.out
echo EPW_WAN_DONE $(date -Is)
