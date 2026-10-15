#!/usr/bin/env python3
"""Read Gamma_alphabeta_s.dat (kernel variant of EPW) and compute per-mode invariants vs photon energy.
Columns per line: omega(eV), Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy  (Angstrom^2/eV).
Invariants written per mode:
  frob  = sqrt(sum_ab |G_ab|^2)      (rotation invariant, primary)
  sumabs = sum_ab |G_ab|
  abssum = |sum_ab G_ab|             (isotropic field E^a=E^b=E0 as in the SI amplitude formula)
Usage: kernel_invariants.py Gamma_alphabeta_s.dat out_prefix"""
import sys, math
fn, out = sys.argv[1], sys.argv[2]
modes = {}  # imode -> (w_meV, [(omega, [9 complex])])
cur = None
for line in open(fn):
    s = line.strip()
    if not s or s.startswith('#'):
        continue
    if s.startswith('imode'):
        parts = s.replace('=', ' ').split()
        cur = int(parts[1]); modes[cur] = (float(parts[2]), [])
        continue
    v = [float(x) for x in s.split()]
    om = v[0]
    g = [complex(v[1 + 2 * i], v[2 + 2 * i]) for i in range(9)]
    modes[cur][1].append((om, g))
summary = []
with open(out + '_invariants.dat', 'w') as f:
    f.write('# per-mode invariants of Gamma^{ab}_s(omega_s; omega,-omega); units Angstrom^2/eV\n')
    f.write('# columns: omega(eV) frob sumabs abssum   [one block per mode; block header gives imode and energy in meV]\n')
    for im in sorted(modes):
        w, rows = modes[im]
        f.write('# imode %d  phonon energy %.6f meV (%.4f THz)\n' % (im, w, w / 4.135667696))
        best = (0.0, None, None, None)
        for om, g in rows:
            frob = math.sqrt(sum(abs(x) ** 2 for x in g))
            sumabs = sum(abs(x) for x in g)
            abssum = abs(sum(g))
            f.write('%10.5f %16.8e %16.8e %16.8e\n' % (om, frob, sumabs, abssum))
            if frob > best[0]:
                best = (frob, om, sumabs, abssum)
        f.write('\n')
        summary.append((im, w, best))
with open(out + '_peaks.txt', 'w') as f:
    f.write('# per-mode maximum of frob = sqrt(sum_ab |Gamma_ab|^2) over the photon-energy grid\n')
    f.write('# imode  w(meV)   w(THz)   omega_peak(eV)  frob_max  sumabs_at_peak  abssum_at_peak\n')
    for im, w, (frob, om, sa, ab) in summary:
        f.write('%5d %10.4f %8.4f %10.4f %14.6e %14.6e %14.6e\n' % (im, w, w / 4.135667696, om if om is not None else -1, frob, sa or 0, ab or 0))
# global maximum over modes
gm = max(summary, key=lambda t: t[2][0])
print('global max of frob: mode %d (%.3f meV = %.4f THz) at omega = %.4f eV, value %.6e A^2/eV' % (gm[0], gm[1], gm[1] / 4.135667696, gm[2][1], gm[2][0]))
for im, w, (frob, om, sa, ab) in summary:
    print('mode %2d  %8.3f meV  peak %.3f eV  frob %.4e  sumabs %.4e  abssum %.4e' % (im, w, om or -1, frob, sa or 0, ab or 0))
