#!/usr/bin/env python3
"""Mesh convergence of the kernel invariant. Usage: mesh_convergence.py N1 N2 ... (reads results/kernel/kN/Gamma_alphabeta_s.dat)
Prints per mesh: peak energy and value of the per-mode Frobenius norm (max over the 3 T2 modes), the total in quadrature,
the plain per-mode sum of magnitudes, and the total at fixed energies. Writes results/kernel/mesh_convergence.dat"""
import sys, math, os
base = '<whiteboard>/GaP_whiteboard/results/kernel'
def load(fn):
    modes = {}; cur = None
    for l in open(fn):
        s = l.split()
        if not s or l.lstrip().startswith('#'): continue
        if s[0] == 'imode': cur = int(s[2]); modes[cur] = {'w': float(s[3]), 'd': []}; continue
        v = [float(x) for x in s]; modes[cur]['d'].append((v[0], [complex(v[1+2*i], v[2+2*i]) for i in range(9)]))
    return modes
def peak(xs, ys):
    i = max(range(len(ys)), key=lambda j: ys[j])
    if 0 < i < len(ys)-1:  # parabolic refinement
        y0, y1, y2 = ys[i-1], ys[i], ys[i+1]; d = (y0 - 2*y1 + y2)
        dx = 0.5*(y0 - y2)/d if d != 0 else 0.0
        return xs[i] + dx*(xs[1]-xs[0]), y1 - 0.25*(y0 - y2)*dx, xs[i], y1
    return xs[i], ys[i], xs[i], ys[i]
rows = []
probe = [2.0, 2.5, 2.8, 2.9, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
out = open(base + '/mesh_convergence.dat', 'w')
out.write('# N  peak_E(grid,eV) peak_total(ang^2/eV) peak_E(parabolic) peak_total(parabolic)  max_per_mode_frob  per_mode_sum|.|(at peak, mode with max)  | total at ' + ' '.join('%.1f' % p for p in probe) + ' eV\n')
for N in sys.argv[1:]:
    fn = '%s/k%s/Gamma_alphabeta_s.dat' % (base, N)
    if not os.path.exists(fn): print('missing', fn); continue
    m = load(fn); ids = sorted(m); om = [o for o, _ in m[ids[0]]['d']]
    frob = {i: [math.sqrt(sum(abs(x)**2 for x in c)) for _, c in m[i]['d']] for i in ids}
    sm = {i: [sum(abs(x) for x in c) for _, c in m[i]['d']] for i in ids}
    tot = [math.sqrt(sum(frob[i][k]**2 for i in ids)) for k in range(len(om))]
    sel = [k for k in range(len(om)) if 0 <= om[k] <= 6.0]
    pe, pv, ge, gv = peak([om[k] for k in sel], [tot[k] for k in sel])
    kpk = sel[max(range(len(sel)), key=lambda j: tot[sel[j]])]
    mode_max = max(ids, key=lambda i: frob[i][kpk])
    vals = []
    for p in probe:
        k = min(range(len(om)), key=lambda j: abs(om[j]-p)); vals.append(tot[k])
    line = '%4s  %.3f %.4f  %.3f %.4f  %.4f %.4f | ' % (N, ge, gv, pe, pv, frob[mode_max][kpk], sm[mode_max][kpk]) + ' '.join('%.3f' % v for v in vals)
    print(line); out.write(line + '\n')
    rows.append((int(N), ge, gv))
out.close()
if len(rows) > 1:
    print('# relative change of the peak total vs. previous mesh:')
    for a, b in zip(rows[:-1], rows[1:]): print('   %d -> %d : %+.2f %%  (peak energy %.2f -> %.2f eV)' % (a[0], b[0], 100*(b[2]-a[2])/a[2], a[1], b[1]))
