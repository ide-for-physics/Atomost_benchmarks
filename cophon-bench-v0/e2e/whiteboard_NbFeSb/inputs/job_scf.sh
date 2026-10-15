#!/bin/bash
#SBATCH --job-name=nbfesb_scf
#SBATCH --account=project_<id>
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --hint=nomultithread
#SBATCH --time=00:45:00
#SBATCH --output=slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun $BIN/pw.x -nk 8 -in scf.in > scf.out || { echo SCF_FAILED; exit 1; }
grep -q "JOB DONE" scf.out || { echo SCF_NOT_DONE; exit 1; }
echo "SCF done $(date -Is)"
# keep copies of the SCF save for the NSCF and the bands runs (ph.x needs the original untouched)
rm -rf tmp_bands tmp_nscf
mkdir -p tmp_bands tmp_nscf
cp -r tmp/nbfesb.save tmp_bands/
cp -r tmp/nbfesb.save tmp_nscf/
srun $BIN/projwfc.x -nk 8 -in projwfc.in > projwfc.out
echo "projwfc done $(date -Is)"
srun $BIN/pw.x -nk 16 -in bands.in > bands.out
echo "bands done $(date -Is)"
# band energies along the path from the xml via bands.x-like extraction: use verbosity=high output
rm -rf tmp_bands/nbfesb.save/wfc*.dat
echo "END $(date -Is)"
