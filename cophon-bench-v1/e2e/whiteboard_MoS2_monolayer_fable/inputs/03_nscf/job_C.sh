#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p small
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -t 01:00:00
#SBATCH -J mos2_C_nscf_bands
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
python3 mkinputs.py
# band structure on a copy of the SCF data (so the NSCF grid wavefunctions stay in ../01_scf/tmp)
rm -rf tmp_bands && mkdir -p tmp_bands && cp -r ../01_scf/tmp/mos2.save tmp_bands/
srun -n 128 $BIN/pw.x -nk 16 -in bands.in > bands.out
echo "BANDS_DONE $(date -Is)"
cat > bandsx.in <<EOF
&bands
  prefix = 'mos2'
  outdir = './tmp_bands'
  filband = 'dft_bands.dat'
  lsym = .false.
/
EOF
srun -n 1 $BIN/bands.x -in bandsx.in > bandsx.out
rm -rf tmp_bands/mos2.save/wfc*.dat tmp_bands/mos2.wfc*
# NSCF on the full coarse grid, in an own copy of the SCF data (EPW reads outdir = ../03_nscf/tmp; ph.x data stay in ../01_scf/tmp)
rm -rf tmp && mkdir -p tmp && cp -r ../01_scf/tmp/mos2.save tmp/
srun -n 128 $BIN/pw.x -nk 16 -in nscf.in > nscf.out
echo "END $(date -Is)"
