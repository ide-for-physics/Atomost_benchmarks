#!/usr/bin/env python3
"""Compare DFT bands (bands.x filband file) with EPW Wannier-interpolated bands (band.eig, same filband layout)
on the same k-path. Reports RMS and max |E_W - E_DFT| over bands whose DFT energy lies in [emin, emax] (absolute eV),
matching Wannier band i to DFT band i+offset (offset = number of excluded low-lying DFT bands).
Usage: compare_bands.py bos.bands.dat band.eig offset emin emax [vbm] [shift_W]
shift_W: constant added to the Wannier energies (EPW band_plot energies are absolute unless the code shifts them).
"""
import sys, math
def read_filband(fn):
    txt = open(fn).read().split('\n'); hdr = txt[0]
    nb = int(hdr.split('nbnd=')[1].split(',')[0]); nk = int(hdr.split('nks=')[1].split('/')[0])
    vals = []
    for l in txt[1:]: vals += l.split()
    E = []; kk = []; i = 0
    for k in range(nk):
        kk.append([float(x) for x in vals[i:i + 3]]); i += 3
        E.append([float(x) for x in vals[i:i + nb]]); i += nb
    return kk, E
dft_fn, wan_fn, off = sys.argv[1], sys.argv[2], int(sys.argv[3])
emin, emax = float(sys.argv[4]), float(sys.argv[5])
vbm = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
shift = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
kd, Ed = read_filband(dft_fn); kw, Ew = read_filband(wan_fn)
assert len(Ed) == len(Ew), (len(Ed), len(Ew))
diffs = []; worst = {}
for ik in range(len(Ed)):
    for ib in range(len(Ew[ik])):
        ed = Ed[ik][ib + off]
        if emin <= ed <= emax:
            d = Ew[ik][ib] + shift - ed; diffs.append(d); worst[ib] = max(worst.get(ib, 0), abs(d))
rms = math.sqrt(sum(d * d for d in diffs) / len(diffs)); mx = max(abs(d) for d in diffs)
print('window [%.2f, %.2f] eV abs = [%.2f, %.2f] rel VBM; %d points: RMS = %.2f meV, max = %.2f meV'
      % (emin, emax, emin - vbm, emax - vbm, len(diffs), rms * 1e3, mx * 1e3))
for ib in sorted(worst):
    print('  W band %2d (DFT %2d): max |dE| = %8.2f meV' % (ib + 1, ib + off + 1, worst[ib] * 1e3))
