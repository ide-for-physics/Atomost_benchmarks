#!/usr/bin/env python3
"""Write RESULT.json from the production kernel file (kernel/Gamma_alphabeta_s.dat) and jobs.log."""
import json, math, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_kernel import read_kernel, invariants, peak

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IRR = {4: 'E', 5: 'E', 6: 'B', 7: 'A', 8: 'E', 9: 'E', 10: 'B', 11: 'A', 12: 'B', 13: 'E', 14: 'E',
       15: 'A', 16: 'B', 17: 'E', 18: 'E'}   # ph.x mode symmetry (phonons/gamma_mode_symmetry_phx.txt)
START = datetime.datetime(2026, 10, 16, 1, 35, tzinfo=datetime.timezone.utc)

modes = read_kernel(os.path.join(ROOT, 'kernel/Gamma_alphabeta_s.dat'))
inv = invariants(modes)
v, om, im = peak(inv, 0.0, 6.0, which=1)
w_mev = modes[im]['w_mev']

# node-hours from jobs.log (last numeric column of non-comment lines)
nh = 0.0
for line in open(os.path.join(ROOT, 'jobs.log')):
    if line.startswith('#') or not line.strip():
        continue
    try:
        nh += float(line.split()[-1])
    except ValueError:
        pass

now = datetime.datetime.now(datetime.timezone.utc)
wall = (now - START).total_seconds() / 3600.0

res = {
    "schema": "cophon-bench.e.result.v1",
    "material": "InPS4_mp20790",
    "kernel_file": "kernel/Gamma_alphabeta_s.dat",
    "peak_ev": round(om, 4),
    "peak_a2_per_ev": round(v, 3),
    "mode_thz": round(w_mev / 4.135667696, 4),
    "mode_irrep": IRR[im],
    "mesh": "96x96x96",
    "cell_angstrom": [[-2.82951505, 2.82951505, 4.48412705],
                      [2.82951505, -2.82951505, 4.48412705],
                      [2.82951505, 2.82951505, -4.48412705]],
    "species": ["In", "P", "S", "S", "S", "S"],
    "positions_crystal": [[0.00000000, 0.00000000, 0.00000000],
                          [0.75000000, 0.25000000, 0.50000000],
                          [0.11291392, 0.56242619, 0.93503726],
                          [0.62738893, 0.17787666, 0.06496274],
                          [0.82212334, 0.88708608, 0.44951227],
                          [0.43757381, 0.37261107, 0.55048773]],
    "node_hours": round(nh, 2),
    "wall_hours": round(wall, 1),
    "model_usd": None,
    "human_touches": 0,
}
with open(os.path.join(ROOT, 'RESULT.json'), 'w') as f:
    json.dump(res, f, indent=1)
    f.write('\n')
print(json.dumps(res, indent=1))
print('peak mode imode=%d, %.3f meV; DONE time %s' % (im, w_mev, now.isoformat()))
