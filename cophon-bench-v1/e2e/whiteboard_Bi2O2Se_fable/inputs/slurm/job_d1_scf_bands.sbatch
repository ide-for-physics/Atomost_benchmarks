#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH -c 1
#SBATCH -t 00:15:00
#SBATCH -J bos_scf_bands
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun -n 128 $BIN/pw.x -nk 32 -in scf.in > scf.out || exit 1
echo "SCF done $(date -Is)"
cp -r tmp tmp_bands
cp -r tmp tmp_nscf
srun -n 128 $BIN/pw.x -nk 32 -in bands.in > bands.out || exit 1
srun -n 1 $BIN/bands.x -in bands_x.in > bands_x.out
echo "BANDS done $(date -Is)"
rm -rf tmp_bands
echo "END $(date -Is)"
