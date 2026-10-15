#!/bin/bash
#SBATCH --job-name=gap_wALL
#SBATCH --account=project_<id>
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=80
#SBATCH --cpus-per-task=1
#SBATCH --time=01:30:00
#SBATCH --output=job_wan_all.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
ROOT=/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP
echo "START $(date -Is)"
for n in A_p13 B_p8 C_s9 D_s13 E_s8; do
  D=$ROOT/wan_$n; mkdir -p $D; cd $D
  ln -sfn $ROOT/run/gap.save gap.save; ln -sfn $ROOT/run/save save
  srun --exact -n 16 -c 1 --cpu-bind=cores $BIN/epw.x -nk 16 -in epw_wan_$n.in > epw_wan_$n.out 2> srun_$n.err &
done
wait
echo "END $(date -Is)"
