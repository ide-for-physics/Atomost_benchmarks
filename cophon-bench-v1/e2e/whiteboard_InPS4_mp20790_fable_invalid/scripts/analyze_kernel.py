#!/usr/bin/env python3
"""Analyse Gamma_alphabeta_s.dat (kernel variant of EPW) for one or more meshes.

File format (from EPW/src/indabs.f90 of the toolchain):
  '# ...' header lines, then per mode (imode = 4..nmodes):
    '     imode = <i> <phonon energy meV>'
    rows: omega(eV)  Re,Im of xx yy zz xy xz yz yx zx zy   (ang^2/eV)
Invariants per mode and photon energy:
  S1  = sum_{ab} |Gamma^{ab}_s|           ("per-mode magnitudes summed over Cartesian channels")
  FRO = sqrt(sum_{ab} |Gamma^{ab}_s|^2)   (Frobenius norm, strictly rotation invariant)
"""
import sys, math

CH = ['xx', 'yy', 'zz', 'xy', 'xz', 'yz', 'yx', 'zx', 'zy']


def read_kernel(fn):
    modes = {}   # imode -> dict(w_mev=..., omega=[...], G=[[complex x9], ...])
    cur = None
    with open(fn) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith('imode'):
                parts = s.replace('=', ' ').split()
                im = int(parts[1]); wm = float(parts[2])
                cur = modes.setdefault(im, {'w_mev': wm, 'omega': [], 'G': []})
                continue
            parts = s.split()
            om = float(parts[0])
            vals = []
            bad = False
            for v in parts[1:]:
                if 'NaN' in v or 'nan' in v.lower() or 'Inf' in v:
                    bad = True; vals.append(float('nan'))
                else:
                    vals.append(float(v))
            if len(vals) != 18:
                raise RuntimeError('bad row in %s: %s' % (fn, s[:80]))
            G = [complex(vals[2 * i], vals[2 * i + 1]) for i in range(9)]
            cur['omega'].append(om)
            cur['G'].append(G)
    return modes


def invariants(modes):
    """returns dict imode -> (omega list, S1 list, FRO list)"""
    out = {}
    for im, d in modes.items():
        S1 = []; FRO = []
        for G in d['G']:
            if any(math.isnan(g.real) or math.isnan(g.imag) for g in G):
                S1.append(float('nan')); FRO.append(float('nan')); continue
            S1.append(sum(abs(g) for g in G))
            FRO.append(math.sqrt(sum(abs(g) ** 2 for g in G)))
        out[im] = (d['omega'], S1, FRO)
    return out


def peak(inv, lo=0.0, hi=6.0, which=1):
    best = (-1.0, None, None)
    for im, (om, S1, FRO) in inv.items():
        arr = S1 if which == 1 else FRO
        for o, v in zip(om, arr):
            if math.isnan(v) or o < lo or o > hi:
                continue
            if v > best[0]:
                best = (v, o, im)
    return best


def main():
    files = sys.argv[1:]
    data = {}
    for fn in files:
        modes = read_kernel(fn)
        inv = invariants(modes)
        data[fn] = (modes, inv)
        print('==== %s' % fn)
        print('modes: %s' % ' '.join('%d(%.2f meV)' % (im, modes[im]['w_mev']) for im in sorted(modes)))
        om = modes[min(modes)]['omega']
        print('omega grid: %d points, %.3f..%.3f eV, step %.4f' % (len(om), om[0], om[-1], om[1] - om[0]))
        v, o, im = peak(inv, which=1)
        print('PEAK S1  (sum_ab |G|): %.6e ang^2/eV at omega = %.4f eV, imode = %d (%.3f meV = %.4f THz)'
              % (v, o, im, modes[im]['w_mev'], modes[im]['w_mev'] / 4.135667696))
        v2, o2, im2 = peak(inv, which=2)
        print('PEAK FRO (sqrt sum|G|^2): %.6e ang^2/eV at omega = %.4f eV, imode = %d (%.3f meV)'
              % (v2, o2, im2, modes[im2]['w_mev']))
        # per-mode maxima
        print(' per-mode max of S1 (omega, value) and FRO:')
        for jm in sorted(inv):
            omj, S1, FRO = inv[jm]
            k = max((i for i in range(len(S1)) if not math.isnan(S1[i])), key=lambda i: S1[i])
            k2 = max((i for i in range(len(FRO)) if not math.isnan(FRO[i])), key=lambda i: FRO[i])
            print('  imode %2d  w=%8.3f meV  S1max %.4e @ %.3f eV   FROmax %.4e @ %.3f eV'
                  % (jm, modes[jm]['w_mev'], S1[k], omj[k], FRO[k2], omj[k2]))
        # channel breakdown at the peak
        G = modes[im]['G'][modes[im]['omega'].index(o)]
        print(' channels at the S1 peak (|G|, Re, Im):')
        for c, g in zip(CH, G):
            print('   %s  %.4e  (%.4e, %.4e)' % (c, abs(g), g.real, g.imag))
        # total over modes (sum over s of S1) spectrum maximum
        tot = {}
        for jm, (omj, S1, FRO) in inv.items():
            for oo, vv in zip(omj, S1):
                if not math.isnan(vv):
                    tot[oo] = tot.get(oo, 0.0) + vv
        oo = max(tot, key=tot.get)
        print(' sum over modes of S1: max %.4e at %.3f eV' % (tot[oo], oo))
    # mesh comparison
    if len(files) >= 2:
        print('==== mesh comparison (S1 of the peak mode of the last file, every 0.25 eV from 2 eV)')
        ref = files[-1]
        v, o, im = peak(data[ref][1], which=1)
        hdr = 'omega(eV) ' + ' '.join('%18s' % fn.split('/')[-2] for fn in files)
        print(hdr)
        omr = data[ref][1][im][0]
        for i, oo in enumerate(omr):
            if oo < 2.0 or abs((oo * 4) - round(oo * 4)) > 1e-6:
                continue
            row = '%8.3f  ' % oo
            for fn in files:
                S1 = data[fn][1][im][1]
                row += '%18.6e' % S1[i]
            print(row)
        print('peak values per file (S1, omega, imode) and rel. change vs previous:')
        prev = None
        for fn in files:
            v, o, im = peak(data[fn][1], which=1)
            v2, o2, im2 = peak(data[fn][1], which=2)
            rel = '' if prev is None else '  rel.change S1 = %+.3f%%' % (100 * (v - prev) / prev)
            print('  %-40s S1 %.6e @ %.3f eV mode %d | FRO %.6e @ %.3f eV mode %d%s' % (fn, v, o, im, v2, o2, im2, rel))
            prev = v


if __name__ == '__main__':
    main()
