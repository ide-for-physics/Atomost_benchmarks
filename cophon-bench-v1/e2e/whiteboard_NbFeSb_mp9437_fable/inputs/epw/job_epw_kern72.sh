#!/bin/bash
#SBATCH --job-name=nfs_kern72
#SBATCH --account=project_<id>
#SBATCH --partition=small
#SBATCH --ntasks=128
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --cpus-per-task=1
#SBATCH --mem=220G
#SBATCH --time=06:00:00
#SBATCH --output=epw_kern72.slurm.out
source ../env.sh
mkdir -p kern72 && cd kern72
for f in ../*.fmt ../nfs.ukk ../nfs.kgmap ../nfs.kmap ../nfs.dyn0 ../nfs.dyn1 ../save ../tmp_nscf; do ln -sfn $f .; done
rm -f selecq.fmt
srun epw.x -nk 128 -in ../epw_kern72.in > ../epw_kern72.out
cp Gamma_alphabeta_s.dat ../Gamma_alphabeta_s_72x72x72.dat
