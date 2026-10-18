#!/usr/bin/env python3
"""Analyse an EPW (kernel variant) Gamma_alphabeta_s.dat file.

File layout (EPW/src/indabs.f90): for imode = 4..nmodes a header line 'imode = N  <phonon energy meV>', then one line per photon
energy: omega(eV), Re,Im of xx, yy, zz, xy, xz, yz, yx, zx, zy  (units ang^2/eV).

Invariants per mode and photon energy:
  I_sum  = sum_{ab} |G_ab|            (task-sheet definition: per-mode magnitudes summed over Cartesian channels)  <- used in RESULT.json
  I_frob = sqrt(sum_{ab} |G_ab|^2)    (Frobenius norm, true rotational invariant)
  I_tr   = |sum_a G_aa|               (trace)
Usage: analyze_kernel.py FILE [emin emax]
"""
import sys, math, json
fn = sys.argv[1]
emin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
emax = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
modes = {}
cur = None
for line in open(fn):
    t = line.split()
    if not t or t[0] == '#':
        continue
    if t[0] == 'imode':
        cur = int(t[2]); modes[cur] = {'w_meV': float(t[3]), 'rows': []}
        continue
    v = [float(x) for x in t]
    if any(math.isnan(x) or math.isinf(x) for x in v):
        continue
    w = v[0]
    c = [complex(v[1 + 2 * i], v[2 + 2 * i]) for i in range(9)]  # xx yy zz xy xz yz yx zx zy
    isum = sum(abs(x) for x in c)
    ifrob = math.sqrt(sum(abs(x) ** 2 for x in c))
    itr = abs(c[0] + c[1] + c[2])
    modes[cur]['rows'].append((w, isum, ifrob, itr, c))
best = {}
for key, idx in (('sum', 1), ('frob', 2), ('trace', 3)):
    b = None
    for m, d in modes.items():
        for r in d['rows']:
            if r[0] < emin - 1e-9 or r[0] > emax + 1e-9:
                continue
            if b is None or r[idx] > b[2]:
                b = (m, r[0], r[idx])
    best[key] = b
print('# modes:', {m: d['w_meV'] for m, d in modes.items()})
for key in ('sum', 'frob', 'trace'):
    m, w, val = best[key]
    print('peak[%s]: mode %d (%.3f meV = %.4f THz) at %.3f eV, value %.6e ang^2/eV' % (key, m, modes[m]['w_meV'], modes[m]['w_meV'] / 4.135667696, w, val))
# per-mode maxima of I_sum
print('# per-mode max of I_sum:')
for m, d in sorted(modes.items()):
    r = max(d['rows'], key=lambda r: r[1])
    print('  mode %d  w=%.3f meV  peak %.3f eV  I_sum=%.6e  I_frob=%.6e  |xx|=%.3e |yy|=%.3e |zz|=%.3e |xy|=%.3e' % (
        m, d['w_meV'], r[0], r[1], r[2], abs(r[4][0]), abs(r[4][1]), abs(r[4][2]), abs(r[4][3])))
# print the peak row components for the sum-invariant peak
m, w, val = best['sum']
r = [r for r in modes[m]['rows'] if abs(r[0] - w) < 1e-9][0]
lab = ['xx', 'yy', 'zz', 'xy', 'xz', 'yz', 'yx', 'zx', 'zy']
print('# components at the peak (mode %d, %.3f eV):' % (m, w))
for l, x in zip(lab, r[4]):
    print('  %s: %+.6e %+.6e i  |.|=%.6e' % (l, x.real, x.imag, abs(x)))
json.dump({'peak_sum': best['sum'], 'peak_frob': best['frob'], 'peak_trace': best['trace'],
           'modes_meV': {m: d['w_meV'] for m, d in modes.items()}}, open(fn + '.peaks.json', 'w'), indent=1)
