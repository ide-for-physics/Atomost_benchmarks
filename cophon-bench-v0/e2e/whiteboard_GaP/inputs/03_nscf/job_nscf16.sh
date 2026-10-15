#!/bin/bash
#SBATCH --job-name=gap_nscf16
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1750M
#SBATCH --time=00:40:00
#SBATCH --output=job_nscf16.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP
mkdir -p $ROOT/run16/gap.save && cd $ROOT/run16
cp $ROOT/run/gap.save/charge-density.dat $ROOT/run/gap.save/data-file-schema.xml gap.save/ 2>/dev/null
cp $ROOT/run/gap.save/*.upf $ROOT/run/gap.save/*.UPF gap.save/ 2>/dev/null
ln -sfn $ROOT/run/save save
echo "START $(date -Is)"
srun --cpu-bind=cores $BIN/pw.x -nk 32 -in nscf16.in > nscf16.out
echo "NSCF16_DONE $(date -Is)"
