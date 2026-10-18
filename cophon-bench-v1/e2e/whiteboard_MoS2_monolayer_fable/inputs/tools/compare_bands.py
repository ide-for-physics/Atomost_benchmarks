#!/usr/bin/env python3
"""Compare DFT bands (QE bands.x filband format) with EPW Wannier-interpolated bands (band.eig, same format),
computed on the identical k-path. Usage:
  compare_bands.py dft_bands.dat band.eig NEXCL EVBM ECBM EMAX [out.dat]
NEXCL: number of low-lying DFT bands excluded from the Wannier model (bands_skipped).
Statistics are given for the valence bands (DFT E <= EVBM+0.01) and for conduction bands with E <= EMAX, plus bins.
Writes a two-column-per-band comparison file for plotting.
"""
import sys, math
def read_filband(fn):
    L = open(fn).read().split('\n')
    h = L[0]
    nb = int(h.split('nbnd=')[1].split(',')[0]); nk = int(h.split('nks=')[1].split('/')[0])
    i = 1; ks = []; E = []
    while len(ks) < nk:
        t = L[i].split(); i += 1
        if len(t) < 3: continue
        ks.append([float(x) for x in t[:3]])
        e = []
        while len(e) < nb:
            e += [float(x) for x in L[i].split()]; i += 1
        E.append(e)
    return ks, E
dft_k, dft = read_filband(sys.argv[1]); epw_k, epw = read_filband(sys.argv[2])
nex = int(sys.argv[3]); evbm = float(sys.argv[4]); ecbm = float(sys.argv[5]); emax = float(sys.argv[6])
assert len(dft) == len(epw), (len(dft), len(epw))
nw = len(epw[0])
# sanity check that the k-points coincide
dk = max(max(abs(a - b) for a, b in zip(k1, k2)) for k1, k2 in zip(dft_k, epw_k))
print('max |k_dft - k_epw| (2pi/alat) = %.2e' % dk)
def stats(sel):
    if not sel: return (float('nan'), float('nan'), 0)
    return (math.sqrt(sum(d * d for d in sel) / len(sel)), max(abs(d) for d in sel), len(sel))
val = []; cond = []; bins = {}
rows = []
for ik in range(len(dft)):
    r = [ik]
    for ib in range(nw):
        ed = dft[ik][nex + ib]; ew = epw[ik][ib]; d = ew - ed
        r += [ed, ew]
        if ed <= evbm + 0.01:
            val.append(d)
        elif ed <= emax:
            cond.append(d)
        b = math.floor((ed - evbm))
        bins.setdefault(b, []).append(d)
    rows.append(r)
print('bands in model: %d (DFT bands %d-%d)' % (nw, nex + 1, nex + nw))
print('valence (E<=EVBM):            RMS = %.2f meV  max = %.2f meV  (n=%d)' % tuple(x * 1000 if i < 2 else x for i, x in enumerate(stats(val))))
print('conduction (ECBM..%.2f eV):  RMS = %.2f meV  max = %.2f meV  (n=%d)' % ((emax,) + tuple(x * 1000 if i < 2 else x for i, x in enumerate(stats(cond)))))
print('per 1-eV bin relative to VBM (bin: RMS meV, max meV, n):')
for b in sorted(bins):
    s = stats(bins[b]); print('  [%+d,%+d) eV: %8.2f %8.2f %5d' % (b, b + 1, s[0] * 1000, s[1] * 1000, s[2]))
if len(sys.argv) > 7:
    with open(sys.argv[7], 'w') as f:
        f.write('# ik  then for each Wannier band: E_DFT E_Wannier (eV); DFT bands %d-%d\n' % (nex + 1, nex + nw))
        for r in rows:
            f.write('%4d ' % r[0] + ' '.join('%.6f' % x for x in r[1:]) + '\n')
