#!/usr/bin/env python3
"""Generate nscf.in (full 12x12x1 grid, explicit list in [0,1)), bands.in (G-M-K-G path) and the
EPW filkf path file, using the relaxed positions in ../01_scf/positions_crystal.txt."""
pos = open('../01_scf/positions_crystal.txt').read().strip()
NK = 12
head = """&control
  calculation = '%s'
  prefix      = 'mos2'
  outdir      = '%s'
  pseudo_dir  = '../pseudos'
  verbosity   = 'high'
/
&system
  ibrav     = 0
  nat       = 3
  ntyp      = 2
  ecutwfc   = 90.0
  occupations = 'fixed'
  nbnd      = %d
  nosym     = .true.
  noinv     = .true.
/
&electrons
  conv_thr        = 1.0d-10
  diago_thr_init  = 5.0d-6
  diago_full_acc  = .true.
/
ATOMIC_SPECIES
Mo 95.95 Mo.upf
S  32.06 S.upf
CELL_PARAMETERS angstrom
  1.59278871 -2.75879097  0.00000000
  1.59278871  2.75879097  0.00000000
  0.00000000  0.00000000 18.12832700
ATOMIC_POSITIONS crystal
%s
"""
# --- uniform grid for EPW
kl = []
for i in range(NK):
    for j in range(NK):
        kl.append((i / NK, j / NK, 0.0))
w = 1.0 / len(kl)
s = head % ('nscf', './tmp', 40, pos)
s += 'K_POINTS crystal\n%d\n' % len(kl)
s += ''.join('  %.10f %.10f %.10f %.10e\n' % (k[0], k[1], k[2], w) for k in kl)
open('nscf.in', 'w').write(s)
# --- high-symmetry path G-M-K-G (crystal coordinates of the 120-degree hexagonal cell)
G = (0.0, 0.0, 0.0); M = (0.5, 0.0, 0.0); K = (1.0 / 3.0, 1.0 / 3.0, 0.0)
def seg(a, b, n, last=False):
    out = []
    for t in range(n + (1 if last else 0)):
        f = t / n
        out.append(tuple(a[i] + f * (b[i] - a[i]) for i in range(3)))
    return out
path = seg(G, M, 60) + seg(M, K, 35) + seg(K, G, 70, last=True)
s = head % ('bands', './tmp_bands', 40, pos)
s += 'K_POINTS crystal\n%d\n' % len(path)
s += ''.join('  %.10f %.10f %.10f 1.0\n' % k for k in path)
open('bands.in', 'w').write(s)
# EPW filkf: crystal coordinates with weights
with open('path_GMKG.kpt', 'w') as f:
    f.write('%d crystal\n' % len(path))
    for k in path:
        f.write('  %.10f %.10f %.10f 1.0\n' % k)
print(len(kl), 'grid points;', len(path), 'path points')
