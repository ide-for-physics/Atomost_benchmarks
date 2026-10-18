# Analyse EPW kernel output Gamma_alphabeta_s.dat (indabs.f90 format).
# Per mode s and photon energy w (0..6 eV): I_s(w) = sum over 9 Cartesian channels of |Gamma^{ab}_s(w)|  (A^2/eV).
# Also reports the Frobenius form sqrt(sum |Gamma|^2) (rotationally invariant) for cross-check.
import math, sys
fn = sys.argv[1]
W0, W1 = 0.0, 6.0
modes = {}
mode = None
for line in open(fn):
    if line.startswith('#') or not line.strip():
        continue
    if 'imode' in line:
        p = line.split()
        mode = int(p[2]); modes[mode] = {'meV': float(p[3]), 'rows': []}
        continue
    v = line.split()
    if len(v) != 19:
        continue
    w = float(v[0])
    vals = [float(x) for x in v[1:]]
    modes[mode]['rows'].append((w, vals))
best = None
nan_rows = 0
summary = {}
for m, d in sorted(modes.items()):
    bm = None
    for w, vals in d['rows']:
        if not (W0 <= w <= W1):
            continue
        if any(math.isnan(x) for x in vals):
            nan_rows += 1
            continue
        I1 = sum(math.hypot(vals[2*i], vals[2*i+1]) for i in range(9))
        I2 = math.sqrt(sum(vals[2*i]**2 + vals[2*i+1]**2 for i in range(9)))
        if bm is None or I1 > bm[0]:
            bm = (I1, w, I2)
        if best is None or I1 > best[0]:
            best = (I1, w, m, d['meV'])
    summary[m] = bm
    if bm:
        print('mode %d  E=%.3f meV (%.3f THz, %.2f cm-1)  max I=%.4f A^2/eV at %.3f eV  (Frobenius %.4f)' % (
            m, d['meV'], d['meV']*0.241798924, d['meV']*8.065544, bm[0], bm[1], bm[2]))
print('NaN rows skipped (w=0 singularity from 1/(hbar w)^2):', nan_rows)
I1, w, m, meV = best
print('PEAK: w = %.3f eV, I = %.4f A^2/eV, mode %d, %.4f THz, %.2f cm-1' % (w, I1, m, meV*0.241798924, meV*8.065544))
