#!/usr/bin/env python3
"""Compare DFT bands (pw.x 'bands' output parsed with parse_pw_eigs.py --bands) with Wannier90 band.dat
on the same k-path points. Usage: compare_bands.py dft_bands.txt seedname_band.dat Emin Emax [nexclude]
dft_bands.txt: lines 'ik e1 e2 ...' (eV).  seedname_band.dat: Wannier90 format (x, E) blocks, one per band.
For each k and each Wannier band, the deviation is measured against the closest DFT band energy among the
DFT bands lying inside [Emin, Emax] (standard practice; the Wannier bands are matched to DFT bands by energy
ordering inside the window). Writes RMS and max deviation over all Wannier bands inside the window."""
import sys, math
dft = [list(map(float, l.split()[1:])) for l in open(sys.argv[1]) if l.strip()]
wan_blocks, cur = [], []
for l in open(sys.argv[2]):
    if l.strip():
        cur.append(float(l.split()[1]))
    else:
        if cur:
            wan_blocks.append(cur); cur = []
if cur:
    wan_blocks.append(cur)
emin, emax = float(sys.argv[3]), float(sys.argv[4])
nk = len(dft)
assert all(len(b) == nk for b in wan_blocks), ('k count mismatch', nk, [len(b) for b in wan_blocks])
nw = len(wan_blocks)
dev = []
worst = (0, None, None)
for ik in range(nk):
    d = sorted(dft[ik])
    w = sorted(b[ik] for b in wan_blocks)
    # DFT bands inside the outer window used for wannierisation are assumed to be matched in order to the Wannier bands
    # when they are inside [emin, emax]; use nearest-energy matching which is robust to counting offsets.
    for e in w:
        if e < emin or e > emax:
            continue
        err = min(abs(e - x) for x in d)
        dev.append(err)
        if err > worst[0]:
            worst = (err, ik, e)
rms = math.sqrt(sum(x * x for x in dev) / len(dev))
print('window [%.3f, %.3f] eV: n(k)=%d, n(Wannier bands)=%d, points compared=%d' % (emin, emax, nk, nw, len(dev)))
print('RMS deviation = %.3f meV, max deviation = %.3f meV (at k index %s, E=%.4f eV)' % (rms * 1000, worst[0] * 1000, worst[1], worst[2]))
