#!/bin/bash
#SBATCH --job-name=nfs_kern96
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=128
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --cpus-per-task=1
#SBATCH --mem=220G
#SBATCH --time=10:00:00
#SBATCH --output=epw_kern96.slurm.out
source ../env.sh
mkdir -p kern96 && cd kern96
for f in ../*.fmt ../nfs.ukk ../nfs.kgmap ../nfs.kmap ../nfs.dyn0 ../nfs.dyn1 ../save ../tmp_nscf; do ln -sfn $f .; done
rm -f selecq.fmt
srun epw.x -nk 128 -in ../epw_kern96.in > ../epw_kern96.out
cp Gamma_alphabeta_s.dat ../Gamma_alphabeta_s_96x96x96.dat
