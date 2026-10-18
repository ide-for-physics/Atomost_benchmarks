#!/usr/bin/env python3
"""Print I_s(w) line shapes near the peaks for several meshes and the tensor components at the peak.
Usage: lineshape.py N1 N2 ... (meshes; files kernel/Gamma_alphabeta_s_NxNxN.dat)"""
import sys, math
labels = ['xx', 'yy', 'zz', 'xy', 'xz', 'yz', 'yx', 'zx', 'zy']
def load(fn):
    modes = {}; cur = None
    for line in open(fn):
        s = line.split()
        if not s or s[0].startswith('#'): continue
        if s[0] == 'imode': cur = int(s[2]); modes[cur] = []; continue
        w = float(s[0]); v = [float(x) for x in s[1:19]]
        c = [complex(v[2 * i], v[2 * i + 1]) for i in range(9)]
        if any(math.isnan(abs(x)) for x in c): continue
        modes[cur].append((w, sum(abs(x) for x in c), c))
    return modes
Ns = [int(x) for x in sys.argv[1:]]
D = {n: load('/home/wb/work/kernel/Gamma_alphabeta_s_%dx%dx%d.dat' % (n, n, n)) for n in Ns}
for mode, lo, hi in [(9, 3.60, 4.00), (12, 2.20, 2.70)]:
    print('mode %d I_sum: w ' % mode + ' '.join('N%d' % n for n in Ns))
    for i, (w, a, c) in enumerate(D[Ns[-1]][mode]):
        if lo <= w <= hi and round(w * 100) % 2 == 0:
            print('  %.2f ' % w + ' '.join('%7.2f' % D[n][mode][i][1] for n in Ns))
for mode in (9, 12, 7, 14):
    n = Ns[-1]
    w, a, c = max(D[n][mode], key=lambda t: t[1])
    print('N%d mode %d peak at %.2f eV, I_sum %.3f: ' % (n, mode, w, a) + ' '.join('%s=%.3f%+.3fi' % (l, x.real, x.imag) for l, x in zip(labels, c)))
