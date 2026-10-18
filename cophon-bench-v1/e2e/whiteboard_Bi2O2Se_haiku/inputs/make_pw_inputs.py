# Generates production pw.x / ph.x inputs for Bi2O2Se from the sealed cell and the relaxed positions.
import itertools
cell = """  -1.96469684   1.96469684   6.20630152
   1.96469684  -1.96469684   6.20630152
   1.96469684   1.96469684  -6.20630152"""
pos = """Bi 0.3531302438 0.3531302438 -0.0000000000
Bi 0.6468697562 0.6468697562 -0.0000000000
Se 0.0000000000 0.0000000000 0.0000000000
O  0.2500000000 0.7500000000 0.5000000000
O  0.7500000000 0.2500000000 0.5000000000"""
species = """Bi 208.98040 Bi.upf
Se 78.971    Se.upf
O  15.9994   O.upf"""
sysblock = """ ibrav       = 0
    nat         = 5
    ntyp        = 3
    ecutwfc     = 90
    ecutrho     = 360
    occupations = 'fixed'
    nbnd        = 44"""
def pwin(calc, kblock, extra_ctrl="", el=""):
    return f""" &control
    calculation = '{calc}'
    prefix      = 'bi2o2se'
    outdir      = './tmp'
    pseudo_dir  = '../pseudos'
    wf_collect  = .true.
{extra_ctrl} /
 &system
    {sysblock}
 /
 &electrons
    conv_thr    = 1.0d-11
    mixing_beta = 0.5
{el} /
ATOMIC_SPECIES
{species}
CELL_PARAMETERS angstrom
{cell}
ATOMIC_POSITIONS crystal
{pos}
{kblock}
"""
open('scf.in','w').write(pwin('scf', "K_POINTS automatic\n8 8 8 0 0 0"))
# explicit full 8x8x8 grid, equal weights (EPW needs the explicit list in [0,1))
pts = list(itertools.product(range(8), repeat=3))
kl = ["K_POINTS crystal", str(len(pts))] + [f"{i/8:.10f} {j/8:.10f} {k/8:.10f} {1/512:.10f}" for i,j,k in pts]
open('nscf.in','w').write(pwin('nscf', "\n".join(kl)))
open('ph.in','w').write(""" &inputph
  prefix   = 'bi2o2se',
  epsil    = .false.,
  outdir   = './tmp'
  fildyn   = 'bi2o2se.dyn'
  ldisp    = .true.
  fildvscf = 'dvscf'
  nq1=1, nq2=1, nq3=1,
  tr2_ph   = 1.0d-13,
 /
""")
open('pp.in','w').write("bi2o2se\n")
print("written")
