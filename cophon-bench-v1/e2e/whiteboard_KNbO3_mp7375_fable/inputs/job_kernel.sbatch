#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -J kno_kernel
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -o slurm-%j.out
# usage: sbatch -p <small|standard> -t HH:MM:SS [--mem=...] --export=ALL,NK=24 job_kernel.sbatch
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
BIN=$T/bin
cd $SLURM_SUBMIT_DIR
D=run_nk${NK}
mkdir -p $D
cd $D
ln -sfn ../tmp tmp
ln -sfn ../save save
# EPW restart files written by the first (epwwrite) run, needed with epwread = .true.
for f in kno.epmatwp crystal.fmt epwdata.fmt vmedata.fmt dmedata.fmt kno.ukk selecq.fmt kno.kgmap kno.kmap; do
  [ -e ../$f ] && ln -sfn ../$f $f
done
cp ../epw_nk${NK}.in epw.in
echo "START $(date -Is) NK=$NK"
srun $BIN/epw.x -npool $SLURM_NTASKS -in epw.in > epw.out
echo "END $(date -Is)"
ls -la
