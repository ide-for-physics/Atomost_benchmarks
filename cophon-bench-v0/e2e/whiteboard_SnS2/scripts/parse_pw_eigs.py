#!/usr/bin/env python3
"""Parse band energies from a pw.x output (verbosity='high').
Usage: parse_pw_eigs.py pw.out [--count E_top] [--bands]
Prints per-band min/max over k, and with --count E_top the max over k of the number of bands below E_top.
With --bands writes k-index, eigenvalues (eV) to stdout (one line per k)."""
import sys, re
fn = sys.argv[1]
txt = open(fn).read()
blocks = re.split(r'\n\s+k =\s*(-?\d+\.\d+)\s*(-?\d+\.\d+)\s*(-?\d+\.\d+)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s*\n', txt)
# blocks: [pre, kx, ky, kz, body, kx, ky, kz, body, ...]
ks, eigs = [], []
for i in range(1, len(blocks), 4):
    k = tuple(float(x) for x in blocks[i:i+3])
    body = blocks[i+3]
    body = body.split('occupation numbers')[0]
    body = body.split('highest')[0]
    body = body.split('Writing')[0]
    vals = []
    for line in body.strip().split('\n'):
        if not line.strip():
            break
        vals += [float(x) for x in re.findall(r'-?\d+\.\d+', line)]
    ks.append(k); eigs.append(vals)
nb = min(len(e) for e in eigs)
eigs = [e[:nb] for e in eigs]
if '--bands' in sys.argv:
    for i, (k, e) in enumerate(zip(ks, eigs)):
        print(i, ' '.join('%.4f' % x for x in e))
    sys.exit()
print('nk =', len(ks), ' nbnd =', nb)
for ib in range(nb):
    col = [e[ib] for e in eigs]
    print('band %2d  min %8.4f  max %8.4f' % (ib + 1, min(col), max(col)))
if '--count' in sys.argv:
    etop = float(sys.argv[sys.argv.index('--count') + 1])
    cnt = [sum(1 for x in e if x < etop) for e in eigs]
    print('bands below %.3f eV: max over k = %d, min over k = %d' % (etop, max(cnt), min(cnt)))
