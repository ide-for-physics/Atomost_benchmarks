#!/usr/bin/env python3
"""Fine-mesh convergence table of the kernel invariant.
Usage: convergence_table.py label1=path1/Gamma_alphabeta_s.dat label2=... 
For each mesh and each optical mode: photon energy of the maximum of frob = sqrt(sum_ab |Gamma_ab|^2) in [0,6] eV,
its value, and the value of frob at a fixed set of photon energies (for point-by-point comparison)."""
import sys, math
def load(fn):
    d = {}; cur = None
    for l in open(fn):
        s = l.split()
        if not s or l.startswith('#'):
            continue
        if s[0] == 'imode':
            cur = int(s[2]); d[cur] = (float(s[3]), []); continue
        v = [float(x) for x in s]
        d[cur][1].append((v[0], math.sqrt(sum(v[1 + 2 * i] ** 2 + v[2 + 2 * i] ** 2 for i in range(9)))))
    return d
data = [(a.split('=')[0], load(a.split('=')[1])) for a in sys.argv[1:]]
modes = sorted(data[0][1])
print('# peak of the Frobenius invariant per mode and mesh (photon energy eV / value Ang^2 eV^-1)')
print('# mesh        ' + '  '.join('mode%d(%.1fmeV)       ' % (m, data[0][1][m][0]) for m in modes))
for lab, d in data:
    row = []
    for m in modes:
        om, val = max(d[m][1], key=lambda t: t[1])
        row.append('%5.2f / %9.3f' % (om, val))
    print('%-12s  ' % lab + '  '.join(row))
print('# mode 8 (A_1g) and mode 4 (E_g) values at fixed photon energies')
grid = [3.90, 3.95, 4.00, 4.05, 4.10, 4.15, 4.20, 5.60, 5.65, 5.70]
print('# mesh        ' + ' '.join('%7.2f' % g for g in grid) + '   | mode 4 at ' + ' '.join('%5.2f' % g for g in grid[-3:]))
for lab, d in data:
    def at(m, g):
        return min(d[m][1], key=lambda t: abs(t[0] - g))[1]
    print('%-12s  ' % lab + ' '.join('%7.2f' % at(8, g) for g in grid) + '   | ' + ' '.join('%7.2f' % at(4, g) for g in grid[-3:]))
