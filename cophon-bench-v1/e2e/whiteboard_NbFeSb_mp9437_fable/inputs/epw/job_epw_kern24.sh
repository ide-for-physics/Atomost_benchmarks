#!/bin/bash
#SBATCH --job-name=nfs_kern24
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --time=01:00:00
#SBATCH --output=epw_kern24.slurm.out
source ../env.sh
mkdir -p kern24 && cd kern24
for f in ../*.fmt ../nfs.ukk ../nfs.kgmap ../nfs.kmap ../nfs.dyn0 ../nfs.dyn1 ../save ../tmp_nscf; do ln -sfn $f .; done
rm -f selecq.fmt
srun epw.x -nk 64 -in ../epw_kern24.in > ../epw_kern24.out
cp Gamma_alphabeta_s.dat ../Gamma_alphabeta_s_24x24x24.dat
