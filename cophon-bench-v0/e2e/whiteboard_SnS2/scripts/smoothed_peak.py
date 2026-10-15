#!/usr/bin/env python3
"""Peak of the Frobenius invariant after a running average over +-w eV (robust against residual mesh noise).
Usage: smoothed_peak.py w_eV label=path ..."""
import sys, math
w = float(sys.argv[1])
def load(fn):
    d = {}; cur = None
    for l in open(fn):
        s = l.split()
        if not s or l.startswith('#'):
            continue
        if s[0] == 'imode':
            cur = int(s[2]); d[cur] = (float(s[3]), []); continue
        v = [float(x) for x in s]
        d[cur][1].append((v[0], math.sqrt(sum(v[1 + 2 * i] ** 2 + v[2 + 2 * i] ** 2 for i in range(9)))))
    return d
print('# running average over +-%.2f eV; per mode: photon energy of max / smoothed value' % w)
for a in sys.argv[2:]:
    lab, fn = a.split('=')
    d = load(fn)
    row = []
    for m in sorted(d):
        pts = d[m][1]
        sm = []
        for i, (om, _) in enumerate(pts):
            sel = [v for o, v in pts if abs(o - om) <= w + 1e-9]
            sm.append((om, sum(sel) / len(sel)))
        om, val = max(sm, key=lambda t: t[1])
        row.append('m%d %5.2f/%7.2f' % (m, om, val))
    print('%-6s ' % lab + '  '.join(row))
