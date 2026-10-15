#!/usr/bin/env python3
"""Post-process Gamma_alphabeta_s.dat (EPW kernel variant). Usage: kernel_analysis.py file [label]
Prints, per optical mode: peak photon energy (0-6 eV) of the Frobenius norm sqrt(sum_ab |G_ab|^2), its value,
the plain sum of magnitudes sum_ab |G_ab|, and writes <file>_invariants.dat with columns
omega, per-mode Frobenius, per-mode sum|.|, total (quadrature over modes)."""
import sys, math
fn = sys.argv[1]; label = sys.argv[2] if len(sys.argv) > 2 else fn
modes = {}; cur = None
for l in open(fn):
    s = l.split()
    if not s or l.lstrip().startswith('#'): continue
    if s[0] == 'imode':
        cur = int(s[2]); modes[cur] = {'w_meV': float(s[3]), 'data': []}; continue
    v = [float(x) for x in s]
    om = v[0]; c = [complex(v[1+2*i], v[2+2*i]) for i in range(9)]  # xx yy zz xy xz yz yx zx zy
    modes[cur]['data'].append((om, c))
names = ['xx','yy','zz','xy','xz','yz','yx','zx','zy']
out = open(fn + '_invariants.dat', 'w')
ids = sorted(modes)
out.write('# omega(eV) ' + ' '.join('frob_m%d sum_m%d' % (m, m) for m in ids) + ' frob_total(quadrature over modes)\n')
nw = len(modes[ids[0]]['data'])
best = {m: (0, 0) for m in ids}; best_tot = (0, 0)
for iw in range(nw):
    om = modes[ids[0]]['data'][iw][0]
    row = [om]; tot2 = 0
    for m in ids:
        c = modes[m]['data'][iw][1]
        fro = math.sqrt(sum(abs(x)**2 for x in c)); sm = sum(abs(x) for x in c)
        row += [fro, sm]; tot2 += fro**2
        if 0 <= om <= 6 and fro > best[m][1]: best[m] = (om, fro)
    tot = math.sqrt(tot2); row.append(tot)
    if 0 <= om <= 6 and tot > best_tot[1]: best_tot = (om, tot)
    out.write(' '.join('%.6f' % x for x in row) + '\n')
out.close()
print('== %s' % label)
for m in ids:
    om, fro = best[m]
    # components at the peak
    c = [x for (o, x) in modes[m]['data'] if abs(o - om) < 1e-6][0]
    comp = ' '.join('%s=%.4g' % (n, abs(x)) for n, x in zip(names, c) if abs(x) > 1e-3 * fro)
    print('mode %d (%.3f meV = %.4f THz): peak Frobenius %.6g ang^2/eV at %.3f eV; sum|.|=%.6g; |comps|: %s'
          % (m, modes[m]['w_meV'], modes[m]['w_meV'] / 4.135667696, fro, om, sum(abs(x) for x in c), comp))
print('all optical modes in quadrature: peak %.6g ang^2/eV at %.3f eV' % (best_tot[1], best_tot[0]))
