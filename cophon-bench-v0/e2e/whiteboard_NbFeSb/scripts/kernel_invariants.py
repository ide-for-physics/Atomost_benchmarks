#!/usr/bin/env python3
"""Parse EPW kernel-variant output Gamma_alphabeta_s.dat and compute rotational invariants per optical mode.

File format (from indabs.f90): header lines starting with '#', then per mode a line
  'imode = <i> <phonon energy meV>' followed by nomega lines:
  omega(eV)  Re,Im of xx yy zz xy xz yz yx zx zy   (ang^2/eV)
Invariants computed for each mode s and photon energy w:
  S1 = sum_{ab} |G_s^{ab}|                 (sum of channel magnitudes; headline quantity)
  F  = sqrt(sum_{ab} |G_s^{ab}|^2)         (Frobenius norm)
  A  = |sum_{ab} G_s^{ab}|                 (isotropic-field combination, SI Sec. IV A)
Usage: kernel_invariants.py Gamma_alphabeta_s.dat [--out prefix]
"""
import sys, math

def parse(fn):
    modes = {}
    order = []
    cur = None
    with open(fn) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith('imode'):
                parts = s.replace('=', ' ').split()
                im = int(parts[1]); wmev = float(parts[2])
                cur = im
                modes[im] = {'w_meV': wmev, 'omega': [], 'G': []}
                order.append(im)
                continue
            v = [float(x.replace('D', 'E')) for x in s.split()]
            if cur is None or len(v) != 19:
                continue
            om = v[0]
            comps = [complex(v[1 + 2 * i], v[2 + 2 * i]) for i in range(9)]
            modes[cur]['omega'].append(om)
            modes[cur]['G'].append(comps)
    return order, modes

LABELS = ['xx', 'yy', 'zz', 'xy', 'xz', 'yz', 'yx', 'zx', 'zy']

def invariants(G):
    S1 = sum(abs(g) for g in G)
    F = math.sqrt(sum(abs(g) ** 2 for g in G))
    A = abs(sum(G))
    return S1, F, A

def main():
    fn = sys.argv[1]
    out = None
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    order, modes = parse(fn)
    rows = []
    print(f"# file: {fn}")
    print("# per-mode peak of S1 = sum_ab |Gamma_s^ab| over the photon grid")
    print("# imode  w_meV  w_THz  omega_peak(eV)  S1_peak  F_peak  A_peak  dominant_channels(|G| at peak)")
    THz = 0.2417989242  # 1 meV = 0.2417989 THz
    total_S1 = None
    for im in order:
        m = modes[im]
        inv = [invariants(G) for G in m['G']]
        if total_S1 is None:
            total_S1 = [0.0] * len(inv)
        for i, (S1, F, A) in enumerate(inv):
            total_S1[i] += S1
        ipk = max(range(len(inv)), key=lambda i: inv[i][0])
        S1, F, A = inv[ipk]
        G = m['G'][ipk]
        chan = sorted(zip(LABELS, [abs(g) for g in G]), key=lambda t: -t[1])[:3]
        chan_s = ','.join(f"{l}:{v:.4g}" for l, v in chan)
        print(f"{im:5d} {m['w_meV']:9.4f} {m['w_meV']*THz:8.4f} {m['omega'][ipk]:9.4f} {S1:12.5e} {F:12.5e} {A:12.5e}  {chan_s}")
        rows.append((im, m, inv))
    # global maximum over modes
    best = None
    for im, m, inv in rows:
        for i, (S1, F, A) in enumerate(inv):
            if best is None or S1 > best[0]:
                best = (S1, im, m['omega'][i], F, A, m['w_meV'])
    print(f"# GLOBAL MAX of S1: mode {best[1]} (w = {best[5]:.4f} meV = {best[5]*THz:.4f} THz) at omega = {best[2]:.4f} eV: S1 = {best[0]:.6e} ang^2/eV, F = {best[3]:.6e}, A = {best[4]:.6e}")
    # sum over all optical modes
    om = modes[order[0]]['omega']
    it = max(range(len(total_S1)), key=lambda i: total_S1[i])
    print(f"# SUM over modes of S1: max {total_S1[it]:.6e} at omega = {om[it]:.4f} eV")
    if out:
        with open(out + '_S1_vs_omega.dat', 'w') as f:
            f.write('# omega(eV) ' + ' '.join(f'S1_mode{im}' for im in order) + ' S1_sum\n')
            for i, w in enumerate(om):
                f.write(f"{w:9.4f} " + ' '.join(f"{invariants(modes[im]['G'][i])[0]:12.5e}" for im in order) + f" {total_S1[i]:12.5e}\n")
        with open(out + '_FA_vs_omega.dat', 'w') as f:
            f.write('# omega(eV) ' + ' '.join(f'F_mode{im} A_mode{im}' for im in order) + '\n')
            for i, w in enumerate(om):
                f.write(f"{w:9.4f} " + ' '.join(f"{invariants(modes[im]['G'][i])[1]:12.5e} {invariants(modes[im]['G'][i])[2]:12.5e}" for im in order) + '\n')

if __name__ == '__main__':
    main()
