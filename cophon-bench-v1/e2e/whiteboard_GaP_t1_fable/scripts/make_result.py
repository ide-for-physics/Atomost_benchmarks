#!/usr/bin/env python3
"""Build RESULT.json from the converged kernel file (kernel/Gamma_alphabeta_s.dat).
Invariant (per mode s): M_s(w) = sum over the 9 Cartesian channels ab of |Gamma^{ab}_s(w)| (complex modulus), ang^2/eV.
peak = max over w in (0,6] eV and over optical modes s of M_s(w); mode = the s realising it (dominant at that energy).
Usage: make_result.py kernel_file mesh node_hours wall_hours"""
import sys, json, numpy as np
sys.path.insert(0, 'scripts')
fn, mesh, nh, wh = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
modes = {}; cur = None
for line in open(fn):
    s = line.split()
    if not s or s[0] == '#': continue
    if s[0] == 'imode':
        cur = (int(s[2]), float(s[3])); modes[cur] = []; continue
    modes[cur].append([float(x) for x in s])
best = None
for (im, wmev), rows in sorted(modes.items()):
    a = np.array(rows); w = a[:, 0]; g = a[:, 1::2] + 1j * a[:, 2::2]
    sel = (w > 0) & (w <= 6.0 + 1e-9)
    M = np.abs(g).sum(axis=1); M[~sel] = -1
    j = int(np.argmax(M))
    if best is None or M[j] > best[0]: best = (float(M[j]), float(w[j]), im, wmev)
peak, pe, im, wmev = best
cell = [[0.0, 2.72358864, 2.72358864], [2.72358864, 0.0, 2.72358864], [2.72358864, 2.72358864, 0.0]]
res = {"schema": "cophon-bench.e.result.v1", "material": "GaP_t1", "kernel_file": "kernel/Gamma_alphabeta_s.dat",
       "peak_ev": round(pe, 3), "peak_a2_per_ev": peak, "mode_thz": round(wmev / 4.135667696, 4), "mode_irrep": "T2",
       "mesh": mesh, "cell_angstrom": cell, "species": ["Ga", "P"],
       "positions_crystal": [[0.25, 0.25, 0.25], [0.0, 0.0, 0.0]],
       "node_hours": nh, "wall_hours": wh, "model_usd": None, "human_touches": 0}
json.dump(res, open('RESULT.json', 'w'), indent=1)
print(json.dumps(res, indent=1)); print("dominant imode", im)
