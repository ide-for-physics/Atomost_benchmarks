#!/usr/bin/env python3
"""Build RESULT.json from kernel/Gamma_alphabeta_s.dat (converged mesh), the sealed cell, jobs.log and the wall time.
Usage: make_result.py <mesh string e.g. 48x48x48> <wall_hours>
"""
import sys, re, json
import numpy as np

mesh = sys.argv[1]; wall_hours = float(sys.argv[2])
fn = "kernel/Gamma_alphabeta_s.dat"
modes, cur = {}, None
for line in open(fn):
    if line.startswith('#'): continue
    m = re.match(r"\s*imode\s*=\s*(\d+)\s+([-\d.Ee+]+)", line)
    if m:
        cur = int(m.group(1)); modes[cur] = {'w': float(m.group(2)), 'rows': []}; continue
    v = line.split()
    if cur is not None and len(v) == 19:
        modes[cur]['rows'].append([float(x) for x in v])
best = None
for s in modes:
    a = np.array(modes[s]['rows']); E = a[:, 0]
    G = a[:, 1::2] + 1j * a[:, 2::2]
    I = np.abs(G).sum(axis=1)
    sel = (E >= 0.0) & (E <= 6.0)
    i = int(np.argmax(np.where(sel, I, -1)))
    if best is None or I[i] > best['I']:
        best = {'s': s, 'E': float(E[i]), 'I': float(I[i]), 'wmev': modes[s]['w']}
irrep = {4: 'E', 5: 'E', 6: 'A1', 7: 'E', 8: 'E', 9: 'A1', 10: 'A2', 11: 'E', 12: 'E', 13: 'E', 14: 'E', 15: 'A1'}
# node-hours from jobs.log
nh = 0.0
for line in open("jobs.log"):
    m = re.search(r"=\s*([\d.]+)\s*nh", line)
    if m and not line.startswith('#'):
        nh += float(m.group(1))
cell = [[-0.00000000, 3.26699347, 2.31667251], [2.82929933, -1.63349673, 2.31667251], [-2.82929933, -1.63349673, 2.31667251]]
species = ["K", "Nb", "O", "O", "O"]
pos = [[0.98508373, 0.98508373, 0.98508373], [0.49617025, 0.49617025, 0.49617025],
       [0.47108675, 0.97007153, 0.47108675], [0.97007153, 0.47108675, 0.47108675], [0.47108675, 0.47108675, 0.97007153]]
res = {
    "schema": "cophon-bench.e.result.v1",
    "material": "KNbO3_mp7375",
    "kernel_file": "kernel/Gamma_alphabeta_s.dat",
    "peak_ev": round(best['E'], 3),
    "peak_a2_per_ev": round(best['I'], 4),
    "mode_thz": round(best['wmev'] / 4.135667696, 4),
    "mode_irrep": irrep[best['s']],
    "mesh": mesh,
    "cell_angstrom": cell,
    "species": species,
    "positions_crystal": pos,
    "node_hours": round(nh, 3),
    "wall_hours": round(wall_hours, 2),
    "model_usd": None,
    "human_touches": 0,
}
json.dump(res, open("RESULT.json", "w"), indent=2)
print(json.dumps(res, indent=2))
print("dominant mode index (EPW numbering):", best['s'])
