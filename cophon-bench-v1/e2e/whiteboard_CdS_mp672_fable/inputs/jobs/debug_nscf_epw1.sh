#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -J cds_epw1
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --mem=200G
#SBATCH -t 00:28:00
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
R=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/CdS_mp672/calc
cd $R/epw
date; echo "== copy scf save"
rm -rf cds.save bands; mkdir -p bands
cp -r ../ph/cds.save ./cds.save
cp -r ../ph/cds.save bands/cds.save
echo "== bands (pw.x along G-M-K-G-A-L-H-A)"
srun $T/bin/pw.x -nk 16 -in bands.in > bands.out 2> bands.err
date; echo "== nscf 9x9x6"
srun $T/bin/pw.x -nk 16 -in nscf.in > nscf.out 2> nscf.err
date; echo "== epw1 (wannierize + epb/epw write + kernel 24x24x13)"
srun $T/bin/epw.x -npool 64 -in epw1.in > epw1.out 2> epw1.err
cp Gamma_alphabeta_s.dat Gamma_alphabeta_s_24x24x13.dat 2>/dev/null
cp Pi_0.dat Pi_0_24x24x13.dat 2>/dev/null
date
ls -la | head -60
