"""Analyse EPW Gamma_alphabeta_s.dat (indabs.f90 layout).

File layout: '#' header lines; per mode a line 'imode = <i> <freq meV>' then nomega lines:
  photon_eV, then Re/Im pairs for xx, yy, zz, xy, xz, yz, yx, zx, zy   (units ang^2/eV)

Invariant (adopted definition, see NOTES.md):
  I_s(w) = sum over the 9 Cartesian channels ab of |Gamma^{ab}_s(w)|
  I(w)   = sum_s I_s(w)
peak = max over w in [0, 6] eV of I(w); mode = argmax_s I_s(peak).
usage: python3 -I kernel_peak.py <file> [wmax_eV]
"""
import sys, math, json

THZ_PER_MEV = 0.2417989242  # 1 meV = 0.241799 THz

def read(path):
    modes = {}
    cur = None
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if s.startswith('imode'):
                parts = s.replace('=', ' ').split()
                cur = int(parts[1])
                modes[cur] = {'freq_mev': float(parts[2]), 'w': [], 'ch': []}
                continue
            vals = [float(x) for x in s.split()]
            assert len(vals) == 19, (len(vals), s[:60])
            modes[cur]['w'].append(vals[0])
            modes[cur]['ch'].append([complex(vals[1 + 2 * k], vals[2 + 2 * k]) for k in range(9)])
    return modes

def analyse(modes, wmax=6.0):
    any_mode = next(iter(modes.values()))
    nw = len(any_mode['w'])
    ws = any_mode['w']
    I_tot = [0.0] * nw
    I_mode = {}
    for m, d in modes.items():
        I_s = [sum(abs(c) for c in d['ch'][iw]) for iw in range(nw)]
        I_mode[m] = I_s
        for iw in range(nw):
            if ws[iw] <= wmax + 1e-9:
                I_tot[iw] += I_s[iw]
    iwp = max((iw for iw in range(nw) if ws[iw] <= wmax + 1e-9), key=lambda iw: I_tot[iw])
    mdom = max(I_mode, key=lambda m: I_mode[m][iwp])
    return {
        'peak_ev': ws[iwp],
        'peak_a2_per_ev': I_tot[iwp],
        'mode_index': mdom,
        'mode_freq_mev': modes[mdom]['freq_mev'],
        'mode_thz': modes[mdom]['freq_mev'] * THZ_PER_MEV,
        'dominant_mode_share': I_mode[mdom][iwp] / I_tot[iwp],
        'nomega': nw,
        'w_first_last_ev': [ws[0], ws[-1]],
        'modes': {m: {'freq_thz': modes[m]['freq_mev'] * THZ_PER_MEV,
                      'I_at_peak': I_mode[m][iwp]} for m in sorted(modes)},
    }

if __name__ == '__main__':
    path = sys.argv[1]
    wmax = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
    res = analyse(read(path), wmax)
    print(json.dumps(res, indent=1))
