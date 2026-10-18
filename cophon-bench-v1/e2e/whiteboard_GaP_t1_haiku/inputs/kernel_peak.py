# Peak of the rotational invariant of Gamma^{ab}_s(omega) per mode.
# Invariant per mode: I_s(w) = sqrt( sum_ab |Gamma^{ab}_s(w)|^2 )  (Frobenius norm of the 3x3 Cartesian tensor).
# Total over modes: I(w) = sum_s I_s(w).  Peak = max over w in (0, 6] eV.
import sys, math
path = sys.argv[1]
rows = []   # (mode, energy, [9 complex])
mode = None
with open(path) as f:
    for line in f:
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        if s.startswith('imode'):
            p = s.split()
            mode = (int(p[2]), float(p[-1]))   # (imode, energy meV)
            continue
        vals = [float(x) for x in s.split()]
        e = vals[0]
        if math.isnan(vals[1]):
            continue
        c = [complex(vals[1 + 2 * i], vals[2 + 2 * i]) for i in range(9)]
        rows.append((mode, e, c))
# group by energy
best = None
by_e = {}
for mode_, e, c in rows:
    if e <= 0.0 or e > 6.0 + 1e-9:
        continue
    I_s = math.sqrt(sum(abs(x) ** 2 for x in c))
    by_e.setdefault(round(e, 6), []).append((mode_, I_s))
out = []
for e in sorted(by_e):
    tot = sum(v for _, v in by_e[e])
    dom = max(by_e[e], key=lambda t: t[1])
    out.append((e, tot, dom))
peak = max(out, key=lambda t: t[1])
print('modes:', sorted({m for m, _ in [(r[0], 0) for r in rows] if m}))
print('peak_ev=%.4f  total_I=%.6f A^2/eV  dominant imode=%d (%.3f meV) I_dom=%.6f' % (peak[0], peak[1], peak[2][0][0], peak[2][0][1], peak[2][1]))
# also per-mode peaks
per = {}
for e, tot, dom in out:
    pass
for mode_ in sorted({m for m, _, _ in rows if m}):
    best_m = max(((e, math.sqrt(sum(abs(x)**2 for x in c))) for m, e, c in rows if m == mode_ and 0 < e <= 6.0 + 1e-9), key=lambda t: t[1])
    print('imode %d: peak at %.4f eV, I_s=%.6f A^2/eV' % (mode_[0], best_m[0], best_m[1]))
