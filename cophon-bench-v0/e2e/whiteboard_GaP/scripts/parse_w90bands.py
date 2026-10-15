#!/usr/bin/env python3
"""Compare wannier90's own interpolated bands (seedname_band.dat, kpoint_path G-X-W-K-G-L with bands_num_points=60,
228 points) with DFT bands at the same k-points (first 228 points of kpath.txt, same construction).
Usage: parse_w90bands.py bands.out gap_band.dat VBM CBM nexclude label"""
import sys, re, math
bands_out, bdat, vbm, cbm, nexcl, label = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
txt = open(bands_out).read()
blocks = re.findall(r"bands \(ev\):\s*\n(.*?)(?=\n\s*k =|\n\s*highest|\n\s*Writing|\Z)", txt, flags=re.S)
dft = [[float(x) for x in re.findall(r"[-]?\d+\.\d+", b.split('occupation')[0])] for b in blocks]
bands = []; cur = []
for l in open(bdat):
    s = l.split()
    if not s:
        if cur: bands.append(cur); cur = []
        continue
    cur.append(float(s[1]))
if cur: bands.append(cur)
nb = len(bands); nk = len(bands[0])
assert nk <= len(dft), (nk, len(dft))
# sanity: exact match expected at coarse points (Gamma = 0, X = 60, L = 227)
for ik in (0, 60, 227):
    if ik < nk: print('check ik=%d: DFT %s | W90 %s' % (ik, ' '.join('%.3f' % x for x in dft[ik][nexcl:nexcl+4]), ' '.join('%.3f' % bands[b][ik] for b in range(4))))
emax = cbm + 6.0
dev = []; dv = []; dc = []; worst = (0, 0, 0); perband = {}
for ik in range(nk):
    d = dft[ik][nexcl:nexcl+nb]
    w = sorted(bands[b][ik] for b in range(nb))
    for ib in range(nb):
        if d[ib] > emax: continue
        x = w[ib] - d[ib]; dev.append(x); (dv if d[ib] <= vbm + 1e-6 else dc).append(x)
        perband.setdefault(ib+1, []).append(x)
        if abs(x) > abs(worst[0]): worst = (x, ik, ib+1)
rms = lambda v: math.sqrt(sum(x*x for x in v)/len(v)) if v else float('nan'); mx = lambda v: max(abs(x) for x in v) if v else float('nan')
print('== %s: nk=%d nb=%d, window VB + CB <= %.2f eV' % (label, nk, nb, emax))
print('ALL   : n=%d RMS=%.2f meV max=%.2f meV' % (len(dev), 1e3*rms(dev), 1e3*mx(dev)))
print('VB    : n=%d RMS=%.2f meV max=%.2f meV' % (len(dv), 1e3*rms(dv), 1e3*mx(dv)))
print('CB<=+6: n=%d RMS=%.2f meV max=%.2f meV' % (len(dc), 1e3*rms(dc), 1e3*mx(dc)))
print('worst %.1f meV at ik=%d band %d' % (1e3*worst[0], worst[1], worst[2]))
print('per band: ' + '; '.join('%d: rms %.1f max %.1f (n=%d)' % (b, 1e3*rms(v), 1e3*mx(v), len(v)) for b, v in sorted(perband.items())))
