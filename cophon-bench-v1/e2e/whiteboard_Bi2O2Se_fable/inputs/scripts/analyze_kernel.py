#!/usr/bin/env python3
"""Analyse an EPW Gamma_alphabeta_s.dat kernel file.
Columns per line: omega(eV), Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy  (Ang^2/eV).
Per mode s and photon energy w we form
  I_s(w)  = sum_{ab} |Gamma^{ab}_s(w)|          (sum of the 9 Cartesian channel magnitudes, 'rotational invariant' used in RESULT.json)
  F_s(w)  = sqrt(sum_{ab} |Gamma^{ab}_s(w)|^2)   (Frobenius norm, for reference)
and report the global maximum over modes and energies in [0, 6] eV.
Usage: analyze_kernel.py file [wmin wmax]
"""
import sys, math
fn = sys.argv[1]
wmin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
wmax = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
labels = ['xx', 'yy', 'zz', 'xy', 'xz', 'yz', 'yx', 'zx', 'zy']
modes = {}   # imode -> (energy_meV, list of (w, [complex x9]))
cur = None
for line in open(fn):
    s = line.split()
    if not s or s[0].startswith('#'):
        continue
    if s[0] == 'imode':
        cur = int(s[2]); modes[cur] = (float(s[3]), [])
        continue
    if cur is None:
        continue
    w = float(s[0]); vals = [float(x) for x in s[1:19]]
    c = [complex(vals[2 * i], vals[2 * i + 1]) for i in range(9)]
    if any(math.isnan(abs(x)) or math.isinf(abs(x)) for x in c):
        continue
    modes[cur][1].append((w, c))
best = None
print('# mode  E_meV  THz   peak_w(eV)  I_sum(A2/eV)  F_frob(A2/eV)  dominant_channels')
for m in sorted(modes):
    E, rows = modes[m]
    pk = None
    for w, c in rows:
        if w < wmin or w > wmax:
            continue
        I = sum(abs(x) for x in c)
        if pk is None or I > pk[1]:
            pk = (w, I, math.sqrt(sum(abs(x) ** 2 for x in c)), c)
    if pk is None:
        continue
    dom = sorted(zip([abs(x) for x in pk[3]], labels), reverse=True)[:3]
    print('%3d %9.4f %7.4f %8.3f %14.6e %14.6e   %s' % (m, E, E / 4.135667696, pk[0], pk[1], pk[2],
          ' '.join('%s=%.3e' % (l, a) for a, l in dom)))
    if best is None or pk[1] > best[1]:
        best = (pk[0], pk[1], pk[2], m, E)
if best:
    print('GLOBAL PEAK: w = %.3f eV, I_sum = %.6e A2/eV (Frobenius %.6e), mode %d, E = %.4f meV = %.4f THz'
          % (best[0], best[1], best[2], best[3], best[4], best[4] / 4.135667696))
