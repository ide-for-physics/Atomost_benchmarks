#!/usr/bin/env python3
"""Explicit uniform k-grid in [0,1) crystal coordinates for the EPW NSCF run (K_POINTS crystal)."""
import sys
n1, n2, n3 = (int(x) for x in sys.argv[1:4])
pts = [(i / n1, j / n2, k / n3) for i in range(n1) for j in range(n2) for k in range(n3)]
w = 1.0 / len(pts)
print("K_POINTS crystal")
print(len(pts))
for p in pts:
    print("  %.10f %.10f %.10f %.10e" % (p[0], p[1], p[2], w))
