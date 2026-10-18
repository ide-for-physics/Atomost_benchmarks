#!/usr/bin/env python3
"""Write scf.in from the final coordinates of relax.out (fixed sealed cell)."""
import re, sys
out = open('relax.out').read()
m = re.search(r'Begin final coordinates(.*?)End final coordinates', out, re.S)
if not m:
    sys.exit('no final coordinates in relax.out')
blk = m.group(1)
pos = []
for line in blk.splitlines():
    t = line.split()
    if len(t) >= 4 and t[0] in ('Mo', 'S'):
        pos.append((t[0], float(t[1]), float(t[2]), float(t[3])))
assert len(pos) == 3, pos
# symmetrise: Mo at z=0 exactly, S at +-z
zs = 0.5 * (pos[1][3] + (1.0 - pos[2][3]))
pos = [('Mo', pos[0][1], pos[0][2], 0.0), ('S', pos[1][1], pos[1][2], zs), ('S', pos[2][1], pos[2][2], 1.0 - zs)]
tmpl = """&control
  calculation   = 'scf'
  prefix        = 'mos2'
  outdir        = './tmp'
  pseudo_dir    = '../pseudos'
  tprnfor       = .true.
  tstress       = .true.
  verbosity     = 'high'
/
&system
  ibrav     = 0
  nat       = 3
  ntyp      = 2
  ecutwfc   = 90.0
  occupations = 'fixed'
  nbnd      = 16
/
&electrons
  conv_thr        = 1.0d-12
  diago_thr_init  = 5.0d-6
  mixing_beta     = 0.5
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
K_POINTS automatic
12 12 1 0 0 0
"""
lines = '\n'.join('%-2s %.10f %.10f %.10f' % p for p in pos)
open('scf.in', 'w').write(tmpl % lines)
open('positions_crystal.txt', 'w').write(lines + '\n')
print(lines)
