#!/usr/bin/env python3
"""Per-mode table of kernel invariants (for REPORT.md). usage: mode_table.py kernel_file [kernel_file ...]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_kernel import read_kernel, invariants

# irreps from ph.x mode-symmetry analysis (phonons/gamma_mode_symmetry_phx.txt), point group S4
IRR = {4: 'E', 5: 'E', 6: 'B', 7: 'A', 8: 'E', 9: 'E', 10: 'B', 11: 'A', 12: 'B', 13: 'E', 14: 'E',
       15: 'A', 16: 'B', 17: 'E', 18: 'E'}
MEV2THZ = 1.0 / 4.135667696
MEV2CM = 8.065543937

for fn in sys.argv[1:]:
    m = read_kernel(fn)
    inv = invariants(m)
    print(fn)
    print('| mode | irrep | w (meV) | w (THz) | w (cm-1) | S1 at 3.10 eV | S1 max | at (eV) | Frobenius at 3.10 eV |')
    print('|---|---|---|---|---|---|---|---|---|')
    for im in sorted(m):
        om, S1, FRO = inv[im]
        i = om.index(3.1)
        k = max((j for j in range(len(S1)) if S1[j] == S1[j]), key=lambda j: S1[j])
        w = m[im]['w_mev']
        print('| %d | %s | %.3f | %.4f | %.2f | %.3f | %.3f | %.2f | %.3f |'
              % (im, IRR[im], w, w * MEV2THZ, w * MEV2CM, S1[i], S1[k], om[k], FRO[i]))
