#!/usr/bin/env python3
"""Generate (a) the explicit uniform k-point list in [0,1) for the EPW nscf (crystal coords),
(b) the BCT2 high-symmetry path (Setyawan-Curtarolo) for pw.x bands and EPW band_plot.
Usage: gen_kpts.py nk1 nk2 nk3 npts_per_segment
Writes: nscf_kpts.txt (K_POINTS crystal block), path_pw.txt (K_POINTS crystal_b), path_epw.txt (filkf format)
"""
import sys, math
nk1, nk2, nk3, nseg = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
# (a) uniform grid, EPW ordering (k1 slowest, k3 fastest), weights 1/N
N = nk1 * nk2 * nk3
with open('nscf_kpts.txt', 'w') as f:
    f.write('K_POINTS crystal\n%d\n' % N)
    for i in range(nk1):
        for j in range(nk2):
            for k in range(nk3):
                f.write('  %.10f  %.10f  %.10f  %.10f\n' % (i / nk1, j / nk2, k / nk3, 1.0 / N))
# (b) BCT2 path in fractional coords of the SC primitive reciprocal basis (c > a)
a = 2 * 1.96469684
c = 2 * 6.20630152
eta = (1 + a * a / (c * c)) / 4
zeta = a * a / (2 * c * c)
pts = {
    'G': (0, 0, 0), 'N': (0, 0.5, 0), 'P': (0.25, 0.25, 0.25), 'S': (-eta, eta, eta),
    'S1': (eta, 1 - eta, -eta), 'X': (0, 0, 0.5), 'Y': (-zeta, zeta, 0.5), 'Y1': (0.5, 0.5, -zeta),
    'Z': (0.5, 0.5, -0.5),
}
path = ['G', 'X', 'Y', 'S', 'G', 'Z', 'S1', 'N', 'P', 'Y1', 'Z']
with open('path_pw.txt', 'w') as f:
    f.write('K_POINTS crystal_b\n%d\n' % len(path))
    for i, lab in enumerate(path):
        p = pts[lab]
        n = nseg if i != len(path) - 1 else 1
        f.write('  %.8f %.8f %.8f %d ! %s\n' % (p[0], p[1], p[2], n, lab))
# explicit list (same points) for EPW filkf and for comparing one-to-one
klist = []
labels = []
for s in range(len(path) - 1):
    p0, p1 = pts[path[s]], pts[path[s + 1]]
    for t in range(nseg):
        x = t / nseg
        klist.append(tuple(p0[d] + (p1[d] - p0[d]) * x for d in range(3)))
        labels.append(path[s] if t == 0 else '')
klist.append(pts[path[-1]]); labels.append(path[-1])
with open('path_epw.txt', 'w') as f:
    f.write('%d crystal\n' % len(klist))
    for p in klist:
        f.write('  %.8f %.8f %.8f  1.0\n' % p)
with open('path_pw_explicit.txt', 'w') as f:
    f.write('K_POINTS crystal\n%d\n' % len(klist))
    for p in klist:
        f.write('  %.8f %.8f %.8f  1.0\n' % p)
with open('path_labels.txt', 'w') as f:
    for i, l in enumerate(labels):
        if l:
            f.write('%d %s\n' % (i, l))
print('wrote', N, 'nscf k-points and', len(klist), 'path points')
