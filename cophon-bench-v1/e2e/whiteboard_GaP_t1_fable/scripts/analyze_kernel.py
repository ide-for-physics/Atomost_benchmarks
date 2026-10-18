#!/usr/bin/env python3
"""Parse EPW (kernel variant) Gamma_alphabeta_s.dat and report the peak of the rotational invariant.
Columns after the photon energy: Re,Im of xx,yy,zz,xy,xz,yz,yx,zx,zy (ang^2/eV).
Invariant used for RESULT.json: per mode s, I_s(w) = sum_{ab} |Gamma^{ab}_s(w)| (sum of magnitudes over the 9 Cartesian channels).
Also printed: Frobenius norm per mode, and the sum over all optical modes."""
import sys, math
fn = sys.argv[1]
emax = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
modes = {}   # imode -> (wmeV, [(E, [complex x9])])
cur = None
for line in open(fn):
    s = line.split()
    if not s or line.lstrip().startswith('#'): continue
    if s[0] == 'imode':
        cur = int(s[2]); modes[cur] = (float(s[3]), [])
        continue
    E = float(s[0]); vals = [float(x) for x in s[1:]]
    c = [complex(vals[2*i], vals[2*i+1]) for i in range(9)]
    modes[cur][1].append((E, c))
labels = ['xx','yy','zz','xy','xz','yz','yx','zx','zy']
best = (0, None, None)
print("mode  w(meV)   w(THz)   peak_E(eV)  sum|G|(A2/eV)  frob(A2/eV)  dominant channels")
for m, (w, data) in sorted(modes.items()):
    pk = max(((E, sum(abs(x) for x in c), math.sqrt(sum(abs(x)**2 for x in c)), c) for E, c in data if E <= emax + 1e-9), key=lambda t: t[1])
    E, S, F, c = pk
    dom = sorted(range(9), key=lambda i: -abs(c[i]))[:3]
    print(f"{m:4d} {w:8.3f} {w/4.135667696:8.4f} {E:10.3f} {S:14.6e} {F:12.6e}  " + ", ".join(f"{labels[i]}={abs(c[i]):.3e}" for i in dom))
    if S > best[0]: best = (S, m, E)
# total over optical modes
tot = {}
for m, (w, data) in modes.items():
    for E, c in data:
        tot[E] = tot.get(E, 0.0) + sum(abs(x) for x in c)
Et = max((E for E in tot if E <= emax + 1e-9), key=lambda E: tot[E])
print(f"\nAll-modes sum of magnitudes: peak {tot[Et]:.6e} A2/eV at {Et:.3f} eV")
print(f"RESULT: peak_ev={best[2]:.3f} peak_a2_per_ev={best[0]:.6e} dominant_mode={best[1]} w={modes[best[1]][0]:.4f} meV = {modes[best[1]][0]/4.135667696:.4f} THz")
