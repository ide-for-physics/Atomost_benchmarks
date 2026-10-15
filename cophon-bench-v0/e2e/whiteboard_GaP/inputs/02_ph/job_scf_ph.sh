#!/bin/bash
#SBATCH --job-name=gap_scf_ph
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1750M
#SBATCH --time=02:00:00
#SBATCH --output=job_scf_ph.%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP/run
echo "START $(date -Is)"
srun --cpu-bind=cores $BIN/pw.x -nk 8 -in scf.in > scf.out
echo "SCF_DONE $(date -Is)"
# keep a copy of the SCF data for the separate band-structure run (bands.x overwrites the xml)
mkdir -p ../run_bands && cp -r gap.save ../run_bands/gap.save
srun --cpu-bind=cores $BIN/ph.x -nk 8 -in ph.in > ph.out
echo "PH_DONE $(date -Is)"
srun -n 1 $BIN/dynmat.x < dynmat_asr.in > dynmat_asr.out
srun -n 1 $BIN/dynmat.x < dynmat_asr_q100.in > dynmat_asr_q100.out
echo "END $(date -Is)"
