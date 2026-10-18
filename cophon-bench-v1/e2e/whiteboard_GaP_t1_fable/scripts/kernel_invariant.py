#!/usr/bin/env python3
"""Analyse EPW kernel-variant output Gamma_alphabeta_s.dat.
Per mode s: M_s(w) = sum over the 9 Cartesian channels ab of |Gamma^{ab}_s(w)| (complex modulus), in ang^2/eV.
Invariant: I(w) = sum over optical modes s of M_s(w). Report its maximum over the photon grid, the photon energy,
and the mode with the largest M_s at that energy.
Usage: kernel_invariant.py file [file2 ...]"""
import sys, numpy as np
def parse(fn):
    modes = {}; cur = None
    for line in open(fn):
        s = line.split()
        if not s or s[0] == '#': continue
        if s[0] == 'imode':
            cur = (int(s[2]), float(s[3])); modes[cur] = []; continue
        modes[cur].append([float(x) for x in s])
    out = {}
    for (im, wmev), rows in modes.items():
        a = np.array(rows); w = a[:, 0]
        g = a[:, 1::2] + 1j * a[:, 2::2]      # nw x 9 : xx yy zz xy xz yz yx zx zy
        out[im] = (wmev, w, g)
    return out
for fn in sys.argv[1:]:
    d = parse(fn)
    ims = sorted(d); w = d[ims[0]][1]
    M = np.array([np.abs(d[im][2]).sum(axis=1) for im in ims])   # nmodes x nw
    I = M.sum(axis=0)
    iw = int(np.argmax(I)); imd = ims[int(np.argmax(M[:, iw]))]
    print(f"# {fn}")
    print(f"  photon grid {w[0]:.3f}..{w[-1]:.3f} eV step {w[1]-w[0]:.4f}; modes {ims} energies(meV) {[round(d[im][0],4) for im in ims]}")
    print(f"  PEAK: I(w)=sum_s sum_ab |Gamma| max = {I[iw]:.6e} ang^2/eV at w = {w[iw]:.3f} eV; dominant mode imode={imd} ({d[imd][0]:.4f} meV = {d[imd][0]/4.135667696:.4f} THz), M_s = {M[ims.index(imd), iw]:.6e}")
    for k, im in enumerate(ims):
        j = int(np.argmax(M[k])); print(f"  mode {im}: max M_s = {M[k, j]:.6e} at {w[j]:.3f} eV; at peak {M[k, iw]:.6e}; |Gamma| channels at peak: " + ' '.join(f"{x:.3e}" for x in np.abs(d[im][2][iw])))
    # secondary maxima of I
    loc = [i for i in range(1, len(I)-1) if I[i] > I[i-1] and I[i] >= I[i+1]]
    loc = sorted(loc, key=lambda i: -I[i])[:5]
    print("  top local maxima of I: " + '; '.join(f"{w[i]:.2f} eV: {I[i]:.4e}" for i in loc))
    F = np.sqrt((np.abs(np.array([d[im][2] for im in ims]))**2).sum(axis=(0, 2)))
    j = int(np.argmax(F)); print(f"  (alt. Frobenius norm over modes+channels: max {F[j]:.6e} at {w[j]:.3f} eV)")
