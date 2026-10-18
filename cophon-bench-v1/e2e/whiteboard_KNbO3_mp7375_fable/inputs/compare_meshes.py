#!/usr/bin/env python3
"""Mesh convergence table of the kernel invariant I_s(E) = sum_ab |Gamma^ab_s(E)|.
Usage: compare_meshes.py kernel/Gamma_alphabeta_s_<mesh>.dat ...
Prints, per file: global peak (mode, E, I), and I of the dominant mode at fixed energies; also the
energy-integrated invariant per mode (less sensitive to mesh noise) for the three strongest modes.
"""
import sys, re
import numpy as np

def load(fn):
    modes, cur = {}, None
    for line in open(fn):
        if line.startswith('#'): continue
        m = re.match(r"\s*imode\s*=\s*(\d+)\s+([-\d.Ee+]+)", line)
        if m:
            cur = int(m.group(1)); modes[cur] = {'w': float(m.group(2)), 'rows': []}; continue
        v = line.split()
        if cur is not None and len(v) == 19:
            modes[cur]['rows'].append([float(x) for x in v])
    out = {}
    for s in modes:
        a = np.array(modes[s]['rows']); E = a[:, 0]
        G = a[:, 1::2] + 1j * a[:, 2::2]
        out[s] = (E, np.abs(G).sum(axis=1), modes[s]['w'])
    return out

files = sys.argv[1:]
data = {f: load(f) for f in files}
print(f"{'file':40s} {'mode':>4} {'E_peak':>7} {'I_peak':>9} | I(mode9) at 3.4 3.6 3.8 4.0 4.5 5.0 eV | int_0^6 I_9 dE | int I_15 | int I_6")
for f in files:
    d = data[f]
    best = max(((s,) + tuple(np.r_[d[s][0][np.argmax(d[s][1])], d[s][1].max()]) for s in d), key=lambda x: x[2])
    E, I9, _ = d[9]
    vals = [I9[np.argmin(np.abs(E - e))] for e in (3.4, 3.6, 3.8, 4.0, 4.5, 5.0)]
    ints = [np.trapz(d[s][1], d[s][0]) for s in (9, 15, 6)]
    print(f"{f:40s} {best[0]:4d} {best[1]:7.3f} {best[2]:9.3f} | " + " ".join(f"{v:7.2f}" for v in vals) + " | " + " ".join(f"{v:8.2f}" for v in ints))
