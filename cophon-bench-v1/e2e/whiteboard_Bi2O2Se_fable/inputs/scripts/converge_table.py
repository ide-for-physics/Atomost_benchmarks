#!/usr/bin/env python3
"""Mesh-convergence table for the kernel: per even mode, the peak photon energy and peak invariant I_s = sum_ab |Gamma^ab_s|
for every kernel/Gamma_alphabeta_s_<mesh>.dat, plus the global peak. Also the odd-mode residual (max I over odd modes).
Usage: converge_table.py file1 file2 ...   (files named ..._NxNxN.dat)
"""
import sys, math, re
labels = ['xx', 'yy', 'zz', 'xy', 'xz', 'yz', 'yx', 'zx', 'zy']
def load(fn):
    modes = {}; cur = None
    for line in open(fn):
        s = line.split()
        if not s or s[0].startswith('#'): continue
        if s[0] == 'imode': cur = int(s[2]); modes[cur] = (float(s[3]), []); continue
        w = float(s[0]); v = [float(x) for x in s[1:19]]
        c = [complex(v[2 * i], v[2 * i + 1]) for i in range(9)]
        if any(math.isnan(abs(x)) for x in c): continue
        modes[cur][1].append((w, c))
    return modes
def peak(rows, wmax=6.0):
    best = None
    for w, c in rows:
        if w > wmax: continue
        I = sum(abs(x) for x in c)
        if best is None or I > best[1]: best = (w, I)
    return best
files = sys.argv[1:]
data = {re.search(r'_(\d+)x\d+x\d+', f).group(1): load(f) for f in files}
meshes = sorted(data, key=int)
even = [7, 8, 9, 12, 14, 15]; odd = [4, 5, 6, 10, 11, 13]
print('mesh      ' + ''.join('%14s' % ('N=' + m) for m in meshes))
for mode in even:
    E = data[meshes[0]][mode][0]
    print('mode %2d (%6.2f meV) peak eV ' % (mode, E) + ''.join('%14.3f' % peak(data[m][mode][1])[0] for m in meshes))
    print('                  I_sum   ' + ''.join('%14.4f' % peak(data[m][mode][1])[1] for m in meshes))
print('odd-mode max I_sum        ' + ''.join('%14.4f' % max(peak(data[m][o][1])[1] for o in odd) for m in meshes))
for m in meshes:
    g = max(((peak(data[m][mode][1]), mode) for mode in even), key=lambda t: t[0][1])
    print('N=%s global peak: mode %d  w = %.3f eV  I_sum = %.4f A2/eV' % (m, g[1], g[0][0], g[0][1]))
