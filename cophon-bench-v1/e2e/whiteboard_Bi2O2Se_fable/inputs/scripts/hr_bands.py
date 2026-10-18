#!/usr/bin/env python3
"""Interpolate bands from a wannier90 *_hr.dat file on an explicit k-path (crystal coords) and compare with DFT
bands from bands.x (filband). Usage: hr_bands.py bos_hr.dat path_epw.txt bos.bands.dat nskip emin emax [vbm]
nskip = number of DFT bands below the Wannier manifold (excluded bands). Energies absolute eV.
"""
import sys, math, cmath
hr_fn, path_fn, dft_fn, nskip = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
emin, emax = float(sys.argv[5]), float(sys.argv[6])
vbm = float(sys.argv[7]) if len(sys.argv) > 7 else 0.0
try:
    import numpy as np
except ImportError:
    np = None
L = open(hr_fn).read().split('\n')
nw = int(L[1]); nr = int(L[2])
deg = []; i = 3
while len(deg) < nr:
    deg += [int(x) for x in L[i].split()]; i += 1
H = {}
for l in L[i:]:
    s = l.split()
    if len(s) < 7: continue
    R = (int(s[0]), int(s[1]), int(s[2])); a, b = int(s[3]) - 1, int(s[4]) - 1
    H.setdefault(R, [[0j] * nw for _ in range(nw)])[a][b] = complex(float(s[5]), float(s[6]))
Rs = list(H.keys())
degmap = dict(zip(Rs, deg)) if len(deg) == len(Rs) else None
# k path
kl = [l.split() for l in open(path_fn).read().split('\n')[1:] if l.strip()]
ks = [(float(s[0]), float(s[1]), float(s[2])) for s in kl]
# DFT
txt = open(dft_fn).read().split('\n'); hdr = txt[0]
nb = int(hdr.split('nbnd=')[1].split(',')[0]); nk = int(hdr.split('nks=')[1].split('/')[0])
vals = []
for l in txt[1:]: vals += l.split()
E = []; j = 0
for k in range(nk):
    j += 3; E.append([float(x) for x in vals[j:j + nb]]); j += nb
assert nk == len(ks), (nk, len(ks))
import numpy as np
Hk_all = []
diffs = []; worst = {}
for ik, k in enumerate(ks):
    Hk = np.zeros((nw, nw), dtype=complex)
    for idx, R in enumerate(Rs):
        ph = cmath.exp(2j * math.pi * (k[0] * R[0] + k[1] * R[1] + k[2] * R[2])) / deg[idx]
        Hk += ph * np.array(H[R])
    w = np.linalg.eigvalsh((Hk + Hk.conj().T) / 2)
    for ib in range(nw):
        ed = E[ik][nskip + ib]
        if emin <= ed <= emax:
            d = w[ib] - ed; diffs.append(d)
            worst[ib] = max(worst.get(ib, 0), abs(d))
rms = math.sqrt(sum(d * d for d in diffs) / len(diffs)); mx = max(abs(d) for d in diffs)
print('%s: nw=%d nR=%d; window [%.2f,%.2f] abs = [%.2f,%.2f] rel VBM; %d pts: RMS %.2f meV, max %.2f meV'
      % (hr_fn, nw, nr, emin, emax, emin - vbm, emax - vbm, len(diffs), rms * 1e3, mx * 1e3))
for ib in sorted(worst):
    print('   W band %2d (DFT %2d): max |dE| = %8.2f meV' % (ib + 1, nskip + ib + 1, worst[ib] * 1e3))
