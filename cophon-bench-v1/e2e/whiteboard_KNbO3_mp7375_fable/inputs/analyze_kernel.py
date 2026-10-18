#!/usr/bin/env python3
"""Analyse Gamma_alphabeta_s.dat written by the kernel-variant EPW.
File layout (see EPW/src/indabs.f90): per mode s (imode = 4..nmodes) a header line
   imode = <s> <phonon energy meV>
followed, for each photon energy, by:
   E(eV)  Re,Im of xx yy zz xy xz yz yx zx zy   [ang^2/eV]
Rotational invariant used for RESULT.json: I_s(E) = sum_{ab} |Gamma^{ab}_s(E)| over the 9 Cartesian channels.
Usage: analyze_kernel.py Gamma_alphabeta_s.dat [Emin Emax]
"""
import sys, re
import numpy as np

fn = sys.argv[1]
emin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
emax = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
modes = {}
cur = None
for line in open(fn):
    if line.startswith('#'):
        continue
    m = re.match(r"\s*imode\s*=\s*(\d+)\s+([-\d.Ee+]+)", line)
    if m:
        cur = int(m.group(1)); modes[cur] = {'wmev': float(m.group(2)), 'rows': []}
        continue
    v = line.split()
    if cur is not None and len(v) == 19:
        modes[cur]['rows'].append([float(x) for x in v])
out = {}
best = None
print(f"{'mode':>4} {'w(meV)':>8} {'w(THz)':>8} {'peak E(eV)':>10} {'I_s(A^2/eV)':>12}  dominant channel")
for s in sorted(modes):
    a = np.array(modes[s]['rows'])
    E = a[:, 0]
    G = a[:, 1::2] + 1j * a[:, 2::2]          # (nE, 9) complex: xx yy zz xy xz yz yx zx zy
    I = np.abs(G).sum(axis=1)
    sel = (E >= emin) & (E <= emax)
    nanrows = np.isnan(I).sum()
    i = np.nanargmax(np.where(sel, I, -1))
    lab = ['xx','yy','zz','xy','xz','yz','yx','zx','zy']
    j = np.argmax(np.abs(G[i]))
    wmev = modes[s]['wmev']
    print(f"{s:4d} {wmev:8.3f} {wmev/4.135667696:8.4f} {E[i]:10.3f} {I[i]:12.5g}  {lab[j]} |G|={abs(G[i,j]):.4g}  (NaN rows: {nanrows})")
    out[s] = (E[i], I[i], wmev)
    if best is None or I[i] > best[1]:
        best = (E[i], I[i], wmev, s)
print(f"\nPEAK: mode {best[3]}  E = {best[0]:.3f} eV  I = {best[1]:.6g} A^2/eV  w = {best[2]:.3f} meV = {best[2]/4.135667696:.4f} THz")
# also total over modes as a function of E (for the report)
Etot = np.array(modes[min(modes)]['rows'])[:, 0]
Itot = sum(np.abs(np.array(modes[s]['rows'])[:, 1::2] + 1j*np.array(modes[s]['rows'])[:, 2::2]).sum(axis=1) for s in modes)
np.savetxt(fn.replace('.dat', '_invariant.dat'),
           np.c_[Etot] + 0*Etot[:, None] if False else np.c_[Etot, np.array([np.abs(np.array(modes[s]['rows'])[:, 1::2] + 1j*np.array(modes[s]['rows'])[:, 2::2]).sum(axis=1) for s in sorted(modes)]).T],
           header="E(eV)  I_s(E)=sum_ab|Gamma^ab_s| for modes " + " ".join(str(s) for s in sorted(modes)), fmt="%.6e")
