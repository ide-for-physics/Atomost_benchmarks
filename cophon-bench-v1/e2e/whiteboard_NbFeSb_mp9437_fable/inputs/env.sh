# environment for the authors' QE 7.5 + modified EPW build on LUMI-C
module load LUMI partition/C PrgEnv-gnu cray-fftw 2>/dev/null
unset MKLROOT
export OMP_NUM_THREADS=1
export T=/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75
export PATH=$T/bin:$PATH
