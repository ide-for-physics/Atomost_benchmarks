# Parse EPW Gamma_alphabeta_s.dat and compute the per-mode rotational invariant I_s(w)=sum_ab |Gamma^ab_s(w)|.
# File layout: block per mode: '    imode =  N  E_meV', then rows: photon_eV followed by 18 reals (Re,Im) for
# xx, yy, zz, xy, xz, yz, yx, xz?->(writer order: 11,22,33,12,13,23,21,31,32).
import sys, cmath
path = sys.argv[1]
blocks = {}
cur = None
for line in open(path):
    s = line.split()
    if not s or s[0].startswith('#'):
        continue
    if s[0] == 'imode' or (len(s) >= 3 and s[0] == 'imode' and s[1] == '='):
        cur = int(s[2]); blocks[cur] = {'E_meV': float(s[3]), 'rows': []}
        continue
    if cur is not None and len(s) == 19:
        blocks[cur]['rows'].append([float(x) for x in s])
out = []
for m in sorted(blocks):
    rows = blocks[m]['rows']
    for r in rows:
        w = r[0]
        vals = [complex(r[1+2*i], r[2+2*i]) for i in range(9)]
        I = sum(abs(v) for v in vals)
        F = sum(abs(v)**2 for v in vals) ** 0.5
        out.append((w, m, blocks[m]['E_meV'], I, F))
peak = max(out, key=lambda t: t[3])
print('modes', sorted(blocks))
print('peak (sum|G|): w=%.3f eV mode=%d E=%.3f meV I=%.6g A^2/eV' % (peak[0], peak[1], peak[2], peak[3]))
pf = max(out, key=lambda t: t[4])
print('peak (Frobenius): w=%.3f eV mode=%d E=%.3f meV F=%.6g' % (pf[0], pf[1], pf[2], pf[4]))
for m in sorted(blocks):
    sub = [t for t in out if t[1] == m]
    b = max(sub, key=lambda t: t[3])
    print('mode %2d E=%7.3f meV  max I=%.4g at w=%.2f eV' % (m, blocks[m]['E_meV'], b[3], b[0]))
