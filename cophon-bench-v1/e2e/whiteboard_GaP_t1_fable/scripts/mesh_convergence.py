#!/usr/bin/env python3
"""Mesh convergence of the kernel: per mesh, the per-mode invariant M_s(w)=sum_ab|Gamma^{ab}_s(w)|, its maximum over
optical modes and photon energies (0,6] eV, the sum over the T2 triplet, the Frobenius norm, and the RMS / max relative
difference of the triplet-summed spectrum between consecutive meshes (whole 0-6 eV range and the 2.5-3.5 eV peak region).
Usage: mesh_convergence.py mesh1:file1 mesh2:file2 ..."""
import sys, numpy as np
def parse(fn):
    modes = {}; cur = None
    for line in open(fn):
        s = line.split()
        if not s or s[0] == '#': continue
        if s[0] == 'imode': cur = (int(s[2]), float(s[3])); modes[cur] = []; continue
        modes[cur].append([float(x) for x in s])
    ims = sorted(modes); w = np.array(modes[ims[0]])[:, 0]
    G = np.array([np.array(modes[im])[:, 1::2] + 1j*np.array(modes[im])[:, 2::2] for im in ims])  # nmode x nw x 9
    return ims, w, G
res = []
print(f"{'mesh':>12s} {'peak_eV':>8s} {'max_s M_s':>10s} {'mode':>5s} {'sum_s M_s':>10s} {'Frobenius':>10s} {'2nd max (eV, sum)':>22s}")
for arg in sys.argv[1:]:
    mesh, fn = arg.split(':'); ims, w, G = parse(fn)
    M = np.abs(G).sum(axis=2)                     # nmode x nw
    sel = (w > 0) & (w <= 6 + 1e-9)
    S = M.sum(axis=0); F = np.sqrt((np.abs(G)**2).sum(axis=(0, 2)))
    k = int(np.argmax(np.where(sel, M, -1).max(axis=0))); s = int(np.argmax(M[:, k]))
    loc = [i for i in range(1, len(S)-1) if S[i] > S[i-1] and S[i] >= S[i+1] and sel[i]]
    loc = sorted(loc, key=lambda i: -S[i])
    sec = f"{w[loc[1]]:.2f}, {S[loc[1]]:.2f}" if len(loc) > 1 else '-'
    print(f"{mesh:>12s} {w[k]:8.3f} {M[s,k]:10.4f} {ims[s][0]:5d} {S[k]:10.4f} {F[k]:10.4f} {sec:>22s}")
    res.append((mesh, w, S, M, F))
print("\nconsecutive-mesh differences of the triplet-summed spectrum S(w)=sum_s M_s(w):")
for (m1, w, S1, M1, F1), (m2, _, S2, M2, F2) in zip(res, res[1:]):
    sel = (w > 0) & (w <= 6)
    pk = (w >= 2.5) & (w <= 3.5)
    d = S2 - S1
    print(f"  {m1} -> {m2}: RMS |dS| / mean S over 0-6 eV = {np.sqrt((d[sel]**2).mean())/S2[sel].mean()*100:.2f} %, "
          f"max |dS|/max S = {np.abs(d[sel]).max()/S2[sel].max()*100:.2f} %, "
          f"2.5-3.5 eV: RMS {np.sqrt((d[pk]**2).mean())/S2[pk].mean()*100:.2f} %; "
          f"Frobenius peak {F1.max():.3f} -> {F2.max():.3f} ({(F2.max()/F1.max()-1)*100:+.2f} %)")
