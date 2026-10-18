#!/usr/bin/env python3
"""Build RESULT.json from the adopted kernel file. Usage: make_result.py kernel_file mesh node_hours wall_hours
peak = global maximum over modes and photon energies (0-6 eV) of I_s(w) = sum_ab |Gamma^ab_s(w)| (nine Cartesian channels).
"""
import sys, json, math
fn, mesh, nh, wall = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
irreps = {4: 'Eu', 5: 'Eu', 6: 'A2u', 7: 'Eg', 8: 'Eg', 9: 'A1g', 10: 'Eu', 11: 'Eu', 12: 'B1g', 13: 'A2u', 14: 'Eg', 15: 'Eg'}
modes = {}; cur = None
for line in open(fn):
    s = line.split()
    if not s or s[0].startswith('#'): continue
    if s[0] == 'imode': cur = int(s[2]); modes[cur] = (float(s[3]), []); continue
    w = float(s[0]); v = [float(x) for x in s[1:19]]
    c = [complex(v[2 * i], v[2 * i + 1]) for i in range(9)]
    if any(math.isnan(abs(x)) for x in c): continue
    if 0.0 <= w <= 6.0:
        modes[cur][1].append((w, sum(abs(x) for x in c)))
best = None
for m, (E, rows) in modes.items():
    for w, I in rows:
        if best is None or I > best[2]: best = (m, w, I, E)
m, w, I, E = best
res = {
  "schema": "cophon-bench.e.result.v1",
  "material": "Bi2O2Se",
  "kernel_file": "kernel/Gamma_alphabeta_s.dat",
  "peak_ev": round(w, 3),
  "peak_a2_per_ev": round(I, 4),
  "mode_thz": round(E / 4.135667696, 4),
  "mode_irrep": irreps[m],
  "mesh": mesh,
  "cell_angstrom": [[-1.96469684, 1.96469684, 6.20630152], [1.96469684, -1.96469684, 6.20630152], [1.96469684, 1.96469684, -6.20630152]],
  "species": ["Bi", "Bi", "Se", "O", "O"],
  "positions_crystal": [[0.35312528, 0.35312528, 0.0], [0.64687472, 0.64687472, 0.0], [0.0, 0.0, 0.0], [0.25, 0.75, 0.5], [0.75, 0.25, 0.5]],
  "node_hours": round(nh, 3),
  "wall_hours": round(wall, 2),
  "model_usd": None,
  "human_touches": 0,
}
json.dump(res, open('/home/wb/work/RESULT.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
print('mode index %d, E = %.4f meV' % (m, E))
