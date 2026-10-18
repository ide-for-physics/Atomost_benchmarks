#!/bin/bash
T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
for f in cds.epmatwp epwdata.fmt crystal.fmt vmedata.fmt dmedata.fmt wigner.fmt selecq.fmt cds.ukk cds.kgmap cds.kmap cds.save epw_mesh_template.in; do [ -e $f ] || ln -s ../epw/$f $f; done
for mesh in 96x96x51; do
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
