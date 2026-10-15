#!/bin/bash
# usage: mk_kernel_job.sh N PARTITION NNODES WALLTIME SRCDIR   (SRCDIR = wan_G_s10 or wan16_G_s10; NK coarse set accordingly)
N=$1; P=$2; NN=$3; WT=$4; SRC=$5
T=<whiteboard>/GaP_whiteboard/inputs/05_epw
NK=12; [ "$SRC" = "wan16_G_s10" ] && NK=16
sed -e "s/NKF/$N/g" -e "s/^  nk1         = 12/  nk1         = $NK/" -e "s/^  nk2         = 12/  nk2         = $NK/" -e "s/^  nk3         = 12/  nk3         = $NK/" $T/epw_kernel_template.in > $T/epw_k$N.in
if [ "$P" = "small" ]; then
  sed -e "s/NKF/$N/g" -e "s/SRCDIR/$SRC/" -e "s/^#SBATCH --partition=PARTITION/#SBATCH --partition=small/" \
      -e "s/^#SBATCH --nodes=NNODES/#SBATCH --ntasks=$((NN*128))/" -e "s/^#SBATCH --ntasks-per-node=128/#SBATCH --mem-per-cpu=1750M/" \
      -e "s/WALLTIME/$WT/" -e "s/^NP=.*/NP=$((NN*128))/" $T/job_epw_kernel_template.sh > $T/job_epw_k$N.sh
else
  sed -e "s/NKF/$N/g" -e "s/SRCDIR/$SRC/" -e "s/PARTITION/$P/" -e "s/NNODES/$NN/g" -e "s/WALLTIME/$WT/" $T/job_epw_kernel_template.sh > $T/job_epw_k$N.sh
fi
echo "wrote $T/epw_k$N.in and $T/job_epw_k$N.sh (coarse nk=$NK, src=$SRC, $P, $NN node(s), $WT)"
