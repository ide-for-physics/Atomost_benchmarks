#!/usr/bin/env python3
"""Parse pw.x output (verbosity high) and print per-band min/max energies over all k-points, plus the energies at Gamma/K/M if present."""
import sys, re
txt = open(sys.argv[1]).read()
blocks = re.findall(r'k =(.*?)\(\s*\d+ PWs\)\s+bands \(ev\):\s*\n(.*?)(?:\n\s*\n)', txt, re.S)
E = []
for b in blocks:
    k = [float(x) for x in re.findall(r'-?\d+\.\d+', b[0])]
    e = [float(x) for x in re.findall(r'-?\d+\.\d+', b[1])]
    E.append((tuple(k[:3]), e))
nb = len(E[0][1]); nk = len(E)
print('nk =', nk, 'nbnd =', nb)
m = re.search(r'highest occupied, lowest unoccupied level \(ev\):\s*([-\d.]+)\s+([-\d.]+)', txt)
if m: print('VBM, CBM =', m.group(1), m.group(2))
print('band   min      max   (eV)')
for ib in range(nb):
    v = [e[1][ib] for e in E]
    print('%3d %8.3f %8.3f' % (ib + 1, min(v), max(v)))
for lab, kk in (('Gamma', (0, 0, 0)),):
    for k, e in E:
        if all(abs(a - b) < 1e-6 for a, b in zip(k, kk)):
            print(lab, ' '.join('%.3f' % x for x in e))
