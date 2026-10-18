#!/bin/bash
#SBATCH -A project_<id>
#SBATCH -p debug
#SBATCH -N 1
#SBATCH --ntasks-per-node=128
#SBATCH -c 1
#SBATCH -t 00:12:00
#SBATCH -J bos_ph_b
#SBATCH -o slurm-%j.out
# Resubmittable recover chunk (max_seconds = 540 inside ph_b.in). Completion = dyn file written and no time-out message.
module load LUMI partition/C PrgEnv-gnu cray-fftw
export OMP_NUM_THREADS=1
BIN=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75/bin
cd $SLURM_SUBMIT_DIR
echo "START $(date -Is)"
n=$(ls ph_b_*.out 2>/dev/null | wc -l); n=$((n+1))
out=ph_b_$n.out
srun -n 128 $BIN/ph.x -nk 32 -in ph_b.in > $out
echo "PH-B chunk $n exit $? $(date -Is)"
if [ -f bos.dyn1 ] && ! grep -q "Maximum CPU time exceeded" $out; then
  srun -n 1 $BIN/dynmat.x -in dynmat.in > dynmat.out
  mkdir -p save
  cp _ph0/bos.phsave/patterns.1.xml save/bos.patterns.1.xml 2>/dev/null
  cp _ph0/bos.dvscf1 save/bos.dvscf_q1 2>/dev/null
  cp _ph0/bos.dvscf_q1 save/bos.dvscf_q1 2>/dev/null
  cp _ph0/bos.dvscf save/bos.dvscf_q1 2>/dev/null
  cp bos.dyn1 save/bos.dyn_q1 2>/dev/null
  ls -laR _ph0 > ph0_listing.txt
  echo "PH COLLECTED"
else
  echo "PH NOT FINISHED - resubmit"
fi
echo "END $(date -Is)"
