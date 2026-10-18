#!/usr/bin/env python3
"""Wannier interpolation quality: DFT bands (pw.x bands.out, verbosity high) vs Wannier bands
obtained from seedname_hr.dat (+ seedname_wsvec.dat, use_ws_distance) along the same k-path.

usage: analyze_bands.py bands.out path.dat seed_hr.dat seed_wsvec.dat out_prefix
Writes out_prefix_dft.dat, out_prefix_wan.dat (index, k-distance, energies) and out_prefix_compare.dat
Reports RMS and max |E_W - E_DFT| for (i) valence bands inside the Wannier manifold and (ii) conduction
bands up to EMAX_CB above the CBM (default 6 eV), matching each Wannier band to the nearest DFT eigenvalue.
"""
import sys, math, re
import numpy as np

EF = 5.7164          # mid-gap reference used in EPW (eV)
EMAX_ABOVE_GAP = 6.0  # conduction bands up to CBM + 6 eV
DIS_WIN_MIN = -4.5    # from the .win file


def read_pw_bands(fn):
    ks = []; es = []
    with open(fn) as f:
        lines = f.readlines()
    i = 0
    nb = None
    for line in lines:
        m = re.search(r'number of Kohn-Sham states=\s*(\d+)', line)
        if m:
            nb = int(m.group(1))
    while i < len(lines):
        if 'bands (ev)' in lines[i]:
            m = re.search(r'k =\s*([-\d.]+)\s*([-\d.]+)\s*([-\d.]+)', lines[i])
            ks.append([float(m.group(j)) for j in (1, 2, 3)])
            vals = []
            i += 1
            while len(vals) < nb:
                s = lines[i].strip()
                if s:
                    vals += [float(x) for x in re.findall(r'-?\d+\.\d+', s)]
                i += 1
            es.append(vals[:nb])
        else:
            i += 1
    return np.array(ks), np.array(es)


def read_hr(fn):
    with open(fn) as f:
        f.readline()
        nw = int(f.readline()); nr = int(f.readline())
        ndeg = []
        while len(ndeg) < nr:
            ndeg += [int(x) for x in f.readline().split()]
        H = {}
        for line in f:
            p = line.split()
            if len(p) < 7:
                continue
            R = (int(p[0]), int(p[1]), int(p[2]))
            m, n = int(p[3]) - 1, int(p[4]) - 1
            H.setdefault(R, np.zeros((nw, nw), complex))[m, n] = complex(float(p[5]), float(p[6]))
    Rs = list(H.keys())
    return nw, Rs, ndeg, H


def read_wsvec(fn, nw):
    T = {}
    with open(fn) as f:
        f.readline()
        while True:
            line = f.readline()
            if not line:
                break
            p = line.split()
            if len(p) != 5:
                continue
            R = (int(p[0]), int(p[1]), int(p[2])); m, n = int(p[3]) - 1, int(p[4]) - 1
            nd = int(f.readline())
            ts = [tuple(int(x) for x in f.readline().split()) for _ in range(nd)]
            T[(R, m, n)] = ts
    return T


def wannier_bands(kred, nw, Rs, ndeg, H, T):
    """kred: (nk,3) reduced coords. Uses use_ws_distance shifts T (in lattice units)."""
    nk = len(kred)
    E = np.zeros((nk, nw))
    # expand into flat lists: lattice vector (R+T), flat index m*nw+n, complex weight H_mn(R)/(ndeg*ndegT)
    vecs = []; idx = []; wts = []
    for iR, R in enumerate(Rs):
        HR = H[R] / ndeg[iR]
        for m in range(nw):
            for n in range(nw):
                if T is None:
                    vecs.append(R); idx.append(m * nw + n); wts.append(HR[m, n])
                else:
                    ts = T[(R, m, n)]
                    for t in ts:
                        vecs.append((R[0] + t[0], R[1] + t[1], R[2] + t[2]))
                        idx.append(m * nw + n); wts.append(HR[m, n] / len(ts))
    vecs = np.array(vecs, float); idx = np.array(idx); wts = np.array(wts, complex)
    for ik, k in enumerate(kred):
        ph = np.exp(2j * math.pi * (vecs @ k)) * wts
        Hk = np.bincount(idx, weights=ph.real, minlength=nw * nw) + 1j * np.bincount(idx, weights=ph.imag, minlength=nw * nw)
        Hk = Hk.reshape(nw, nw)
        Hk = 0.5 * (Hk + Hk.conj().T)
        E[ik] = np.linalg.eigvalsh(Hk)
    return E


def main():
    fb, fpath, fhr, fws, pref = sys.argv[1:6]
    kcart, Edft = read_pw_bands(fb)
    kred = np.loadtxt(fpath, skiprows=1)[:, :3]
    assert len(kred) == len(Edft), (len(kred), len(Edft))
    nw, Rs, ndeg, H = read_hr(fhr)
    T = read_wsvec(fws, nw) if fws != 'none' else None
    Ew = wannier_bands(kred, nw, Rs, ndeg, H, T)
    # k-distance along the path (cartesian, 2pi/alat units from pw.x)
    d = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(kcart, axis=0), axis=1))])
    vbm = Edft[Edft < EF].max(); cbm = Edft[Edft > EF].min()
    print('DFT along path: VBM %.4f eV, CBM %.4f eV, gap %.4f eV (EF ref %.4f)' % (vbm, cbm, cbm - vbm, EF))
    # Wannier manifold valence bands: DFT bands with E > DIS_WIN_MIN and E < EF
    nk = len(kred)
    dev_v = []; dev_c = []; rows = []
    for ik in range(nk):
        ed = Edft[ik]; ew = Ew[ik]
        for e in ew:
            if e > cbm + EMAX_ABOVE_GAP + 1e-9:
                continue
            j = np.argmin(np.abs(ed - e))
            dv = e - ed[j]
            rows.append((ik, d[ik], e, ed[j], dv))
            if e < EF:
                dev_v.append(dv)
            else:
                dev_c.append(dv)
    dev_v = np.array(dev_v); dev_c = np.array(dev_c); dev_a = np.concatenate([dev_v, dev_c])
    nv_expected = int(np.sum((Edft[0] > DIS_WIN_MIN) & (Edft[0] < EF)))
    print('Wannier bands below EF per k: %d (DFT bands in window below EF at k0: %d)' %
          (int(np.sum(Ew[0] < EF)), nv_expected))
    for name, arr in (('valence (in Wannier manifold)', dev_v),
                      ('conduction up to CBM+%.0f eV' % EMAX_ABOVE_GAP, dev_c), ('all of the above', dev_a)):
        print('%-34s N=%5d  RMS = %.3f meV  max|dev| = %.3f meV  mean = %+.3f meV' %
              (name, len(arr), 1e3 * math.sqrt(np.mean(arr ** 2)), 1e3 * np.max(np.abs(arr)), 1e3 * np.mean(arr)))
    # windowed stats: conduction up to CBM+3, CBM+4.5
    for emax in (3.0, 4.5):
        sel = np.array([r[4] for r in rows if EF < r[2] <= cbm + emax])
        print('conduction up to CBM+%.1f eV: N=%d RMS %.3f meV max %.3f meV' %
              (emax, len(sel), 1e3 * math.sqrt(np.mean(sel ** 2)), 1e3 * np.max(np.abs(sel))))
    with open(pref + '_dft.dat', 'w') as f:
        f.write('# ik  kdist(2pi/alat)  DFT eigenvalues (eV), %d bands\n' % Edft.shape[1])
        for ik in range(nk):
            f.write('%4d %10.6f ' % (ik, d[ik]) + ' '.join('%9.4f' % e for e in Edft[ik]) + '\n')
    with open(pref + '_wan.dat', 'w') as f:
        f.write('# ik  kdist(2pi/alat)  Wannier-interpolated eigenvalues (eV), %d bands (hr.dat + wsvec)\n' % nw)
        for ik in range(nk):
            f.write('%4d %10.6f ' % (ik, d[ik]) + ' '.join('%9.4f' % e for e in Ew[ik]) + '\n')
    with open(pref + '_compare.dat', 'w') as f:
        f.write('# ik kdist E_wannier(eV) E_dft_nearest(eV) dev(meV)   [Wannier bands up to CBM+%.0f eV]\n' % EMAX_ABOVE_GAP)
        for r in rows:
            f.write('%4d %10.6f %10.4f %10.4f %9.3f\n' % (r[0], r[1], r[2], r[3], 1e3 * r[4]))
    # worst points
    worst = sorted(rows, key=lambda r: -abs(r[4]))[:8]
    print('worst deviations (ik, E_w, E_dft, dev meV):')
    for r in worst:
        print('  %3d %9.4f %9.4f %8.2f' % (r[0], r[2], r[3], 1e3 * r[4]))


if __name__ == '__main__':
    main()
