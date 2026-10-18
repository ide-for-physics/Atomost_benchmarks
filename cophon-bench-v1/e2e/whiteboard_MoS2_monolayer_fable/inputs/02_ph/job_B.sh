#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p small
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -t 01:30:00
#SBATCH -J mos2_B_phG
#SBATCH -o slurm-%j.out
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
srun -n 128 $BIN/ph.x -nk 8 -in ph.in > ph.out
echo "PH_DONE $(date -Is)"
# dynmat.x: frequencies without and with the acoustic sum rule (+ irreps, IR activity)
for a in no simple crystal; do
cat > dynmat_$a.in <<EOF
&input
  fildyn = 'mos2.dyn1'
  asr    = '$a'
  filout = 'dynmat_$a.modes'
  fileig = 'dynmat_$a.eig'
/
EOF
srun -n 1 $BIN/dynmat.x -in dynmat_$a.in > dynmat_$a.out
done
# EPW save/ directory (what EPW/bin/pp.py would produce for a 1-q-point run)
mkdir -p save
cp mos2.dyn1 save/mos2.dyn_q1
cp mos2.dyn0 save/
P=../01_scf/tmp/_ph0
ls -la $P
DV=$(ls $P/mos2.dvscf* | head -1)
cp $DV save/mos2.dvscf_q1
cp -r $P/mos2.phsave save/
ls -la save
echo "END $(date -Is)"
