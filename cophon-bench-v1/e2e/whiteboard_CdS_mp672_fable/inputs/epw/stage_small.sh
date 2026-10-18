#!/bin/bash
# Runs inside the full-node small-partition job (128 ranks). Requires READY (epw1 validated).
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
[ -f READY ] || { echo "not READY"; exit 0; }
# do not overlap with the first-stage debug job in the same directory
while squeue -h -j 22921847 -o '%T' 2>/dev/null | grep -q -E 'RUNNING|PENDING'; do echo "waiting for 22921847 $(date)"; sleep 60; done
# wavefunctions are no longer needed (Wannier data in *.fmt / epmatwp / ukk)
rm -f cds.wfc* cds.save/wfc*.dat; rm -rf bands/cds.save
# DFT bands on exactly the W90 band-plot k-points (for the interpolation-quality comparison)
if [ ! -f bands_w90.out ]; then mkdir -p bands_w90; cp -r cds.save bands_w90/; srun $T/bin/pw.x -nk 32 -in bands_w90.in > bands_w90.out 2> bands_w90.err; rm -rf bands_w90/cds.save; fi
for mesh in $(cat MESHES); do
  n1=${mesh%%x*}; rest=${mesh#*x}; n2=${rest%%x*}; n3=${rest#*x}
  tag=${n1}x${n2}x${n3}
  [ -f Gamma_alphabeta_s_${tag}.dat ] && { echo "skip $tag (done)"; continue; }
  sed -e "s/NK1/$n1/" -e "s/NK2/$n2/" -e "s/NK3/$n3/" epw_mesh_template.in > epw_${tag}.in
  echo "== epw $tag start $(date)"
  srun $T/bin/epw.x -npool 128 -in epw_${tag}.in > epw_${tag}.out 2> epw_${tag}.err
  cp Gamma_alphabeta_s.dat Gamma_alphabeta_s_${tag}.dat
  cp Pi_0.dat Pi_0_${tag}.dat
  echo "== epw $tag end $(date)"
done
