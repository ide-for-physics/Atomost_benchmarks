#!/usr/bin/env python3
"""Compare DFT bands (pw.x 'bands' run at the W90 path k-points, verbosity high) with Wannier bands (seedname_band.dat).
Usage: compare_bands.py bands_wk.out seed_band.dat nexclude vbm cbm emax_above_cbm"""
import sys, re, numpy as np
out, wdat, nex, vbm, cbm, dE = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
txt = open(out).read()
blocks = re.findall(r'k =\s*([-\d\.]+)\s*([-\d\.]+)\s*([-\d\.]+)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s*\n\n((?:\s*[-\d\.]+)+)', txt)
E = np.array([[float(x) for x in b[3].split()] for b in blocks])      # nk x nbnd
W = []
cur = []
for line in open(wdat):
    s = line.split()
    if not s:
        if cur: W.append(cur); cur = []
        continue
    cur.append(float(s[1]))
if cur: W.append(cur)
W = np.array(W).T   # nk x nwann
nk, nw = W.shape
assert nk == E.shape[0], (nk, E.shape)
D = E[:, nex:nex+nw]   # DFT bands matched index-wise to the Wannier bands (lowest nw bands after exclusion)
emax = cbm + dE
diff = W - D
valence = D <= vbm + 1e-3
cond = (D >= cbm - 1e-3) & (D <= emax)
def stats(mask, name):
    d = diff[mask]
    print(f"{name:40s} n={d.size:5d}  RMS={np.sqrt((d**2).mean())*1000:8.3f} meV  max|dev|={np.abs(d).max()*1000:8.3f} meV")
stats(valence, "valence bands (<= VBM)")
stats(cond, f"conduction bands CBM..CBM+{dE} eV")
stats(valence | cond, "both")
for e2 in (2.0, 4.0, 5.0, 6.0, 7.0):
    m = (D >= cbm - 1e-3) & (D <= cbm + e2)
    stats(m, f"  conduction CBM..CBM+{e2} eV")
