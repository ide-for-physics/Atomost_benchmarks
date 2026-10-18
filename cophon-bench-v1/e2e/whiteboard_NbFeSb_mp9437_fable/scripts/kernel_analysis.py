#!/usr/bin/env python3
"""Parse EPW (kernel variant) Gamma_alphabeta_s.dat and report per-mode invariants.
Columns after the photon energy: Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy (ang^2/eV).
Invariant used for RESULT.json: I_s(w) = sum_{ab} |Gamma^{ab}_s(w)| over the 9 Cartesian channels.
Also reports the Frobenius norm F_s(w) = sqrt(sum_{ab} |Gamma^{ab}_s|^2).
"""
import sys, numpy as np
fn = sys.argv[1]
wmax = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
modes = {}
cur = None
for line in open(fn):
    s = line.split()
    if not s or line.lstrip().startswith('#'):
        continue
    if s[0] == 'imode':
        cur = int(s[2]); freq_mev = float(s[3]); modes[cur] = {'freq_mev': freq_mev, 'rows': []}
        continue
    if cur is None:
        continue
    v = np.array([float(x) for x in s])
    modes[cur]['rows'].append(v)
labels = ['xx','yy','zz','xy','xz','yz','yx','zx','zy']
summary = []
for m in sorted(modes):
    A = np.array(modes[m]['rows'])
    w = A[:, 0]
    G = A[:, 1::2] + 1j * A[:, 2::2]   # (nw, 9)
    sel = (w <= wmax + 1e-9)
    I = np.abs(G).sum(axis=1)
    F = np.sqrt((np.abs(G)**2).sum(axis=1))
    i = np.argmax(np.where(sel, I, -1))
    j = np.argmax(np.where(sel, F, -1))
    modes[m].update(w=w, G=G, I=I, F=F)
    summary.append((m, modes[m]['freq_mev'], w[i], I[i], w[j], F[j], labels[np.argmax(np.abs(G[i]))], np.abs(G[i]).max()))
print(f"# file {fn}; invariant I_s = sum_ab |Gamma^ab_s| ; F_s = Frobenius norm; window 0..{wmax} eV")
print("# mode  freq(meV)  freq(THz)   w_peak(I)  I_peak(A^2/eV)   w_peak(F)  F_peak   dominant_channel |G|")
for m, fmev, wi, Ii, wj, Fj, lab, gmax in summary:
    print(f"{m:4d} {fmev:10.4f} {fmev/4.135667696:9.4f} {wi:10.3f} {Ii:14.6e} {wj:10.3f} {Fj:12.6e}   {lab} {gmax:12.6e}")
best = max(summary, key=lambda t: t[3])
print(f"# GLOBAL: mode {best[0]} ({best[1]:.4f} meV = {best[1]/4.135667696:.4f} THz) peak at {best[2]:.3f} eV, I = {best[3]:.6e} A^2/eV")
