#!/usr/bin/env python3
"""Compare DFT bands (pw.x bands.out, verbosity high) with EPW-interpolated bands (band.eig from band_plot)
on the SAME explicit k-list. Usage: parse_bands.py bands.out band.eig VBM CBM nexclude out_prefix
Window for statistics: valence bands (all 4 sp3 VBs) + conduction bands up to CBM + 6 eV.
"""
import sys, re, math
bands_out, band_eig, vbm, cbm, nexcl, outp = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
# --- DFT
txt = open(bands_out).read()
blocks = re.findall(r'k =\s*([-\d\.]+)\s*([-\d\.]+)\s*([-\d\.]+)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s*\n(.*?)(?=\n\s*k =|\n\s*Writing|\n\s*highest|\Z)', txt, flags=re.S)
dft = []
for kx,ky,kz,body in blocks:
    body = body.split('occupation')[0]
    e = [float(x) for x in re.findall(r'[-]?\d+\.\d+', body)]
    dft.append(e)
# --- EPW band.eig : header then per k: a line with 3 coords, then energies (10 per line)
lines = open(band_eig).read().split('\n')
m = re.search(r'nbnd=\s*(\d+),\s*nks=\s*(\d+)', lines[0]); nb, nk = int(m.group(1)), int(m.group(2))
vals = []
for l in lines[1:]:
    vals += [float(x) for x in l.split()]
epw = []
i = 0
for ik in range(nk):
    i += 3  # skip xk
    epw.append(vals[i:i+nb]); i += nb
assert len(dft) == nk, (len(dft), nk)
# --- statistics: DFT bands nexcl+1 .. matched to EPW bands 1..nb (Wannier manifold starts at first VB)
emax = cbm + 6.0
dev_all = []; dev_v = []; dev_c = []; worst = (0, None, None)
rows = []
for ik in range(nk):
    d = dft[ik][nexcl:nexcl+nb]; w = epw[ik]
    row = []
    for ib in range(nb):
        if d[ib] > emax: continue
        x = w[ib] - d[ib]
        dev_all.append(x); (dev_v if d[ib] <= vbm + 1e-6 else dev_c).append(x)
        if abs(x) > abs(worst[0]): worst = (x, ik, ib)
        row.append((d[ib], w[ib]))
    rows.append(row)
rms = lambda v: math.sqrt(sum(x*x for x in v)/len(v)) if v else float('nan')
mx = lambda v: max(abs(x) for x in v) if v else float('nan')
print('k-points %d, Wannier bands %d, window: VB + CB up to CBM+6 eV = %.3f eV' % (nk, nb, emax))
print('ALL   : n=%d RMS=%.2f meV  max=%.2f meV' % (len(dev_all), 1e3*rms(dev_all), 1e3*mx(dev_all)))
print('VB    : n=%d RMS=%.2f meV  max=%.2f meV' % (len(dev_v), 1e3*rms(dev_v), 1e3*mx(dev_v)))
print('CB<=+6: n=%d RMS=%.2f meV  max=%.2f meV' % (len(dev_c), 1e3*rms(dev_c), 1e3*mx(dev_c)))
print('worst: %.2f meV at k index %d band %d' % (1e3*worst[0], worst[1], worst[2]+1))
with open(outp + '_band_compare.dat', 'w') as f:
    f.write('# ik  band  E_DFT(eV)  E_Wannier(eV)  diff(meV)   [bands counted from the first Wannier band = first sp3 valence band; only bands <= CBM+6 eV]\n')
    for ik in range(nk):
        d = dft[ik][nexcl:nexcl+nb]; w = epw[ik]
        for ib in range(nb):
            if d[ib] > emax: continue
            f.write('%5d %4d %12.6f %12.6f %10.3f\n' % (ik, ib+1, d[ib], w[ib], 1e3*(w[ib]-d[ib])))
