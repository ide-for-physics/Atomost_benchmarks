#!/usr/bin/env python3
"""Compare DFT bands (pw.x 'bands' output, verbosity='high') with EPW Wannier-interpolated bands (band.eig)
along the same k list. Reports RMS and max |dE| inside an energy window [emin, emax] (eV, absolute energies).
Usage: band_compare.py bands.out band.eig emin emax [--out file] [--skip N]
  --skip N : number of lowest DFT bands to drop (e.g. semicore bands not Wannierized)
"""
import sys, math, re

def read_pw_bands(fn):
    ks = []; bands = []
    with open(fn) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith('k =') and 'bands (ev)' in lines[i]:
            kline = lines[i]
            m = re.findall(r'[-]?\d+\.\d+', kline.split('(')[0])
            ks.append(tuple(float(x) for x in m[:3]))
            i += 2
            e = []
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('k =', 'occupation', 'highest', 'Writing')):
                e += [float(x) for x in re.findall(r'[-]?\d+\.\d+', lines[i])]
                i += 1
            bands.append(e)
        else:
            i += 1
    return ks, bands

def read_epw_bandeig(fn):
    with open(fn) as f:
        lines = f.readlines()
    hdr = lines[0]
    nb = int(re.search(r'nbnd=\s*(\d+)', hdr).group(1)); nk = int(re.search(r'nks=\s*(\d+)', hdr).group(1))
    ks = []; bands = []
    i = 1
    for ik in range(nk):
        ks.append(tuple(float(x) for x in lines[i].split()[:3])); i += 1
        e = []
        while len(e) < nb:
            e += [float(x) for x in lines[i].split()]; i += 1
        bands.append(e)
    return ks, bands

def main():
    pw, ep, emin, emax = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    skip = int(sys.argv[sys.argv.index('--skip') + 1]) if '--skip' in sys.argv else 0
    kp, bp = read_pw_bands(pw)
    ke, be = read_epw_bandeig(ep)
    assert len(kp) == len(ke), f"k count mismatch {len(kp)} vs {len(ke)}"
    diffs = []; nmatch = 0
    rows = []
    for ik in range(len(kp)):
        dft = sorted(bp[ik])[skip:]
        wan = sorted(be[ik])
        # match DFT bands within the window to the nearest Wannier band of the same ordinal (both sorted)
        for ib, e in enumerate(dft):
            if e < emin or e > emax:
                continue
            if ib >= len(wan):
                continue
            d = wan[ib] - e
            diffs.append(d); nmatch += 1
            rows.append((ik + 1, ib + 1 + skip, e, wan[ib], d))
    rms = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    mx = max(abs(d) for d in diffs)
    imx = max(range(len(diffs)), key=lambda i: abs(diffs[i]))
    print(f"# window [{emin},{emax}] eV: N={nmatch} (k,band) pairs, RMS = {rms*1000:.3f} meV, MAX = {mx*1000:.3f} meV at k#{rows[imx][0]} band {rows[imx][1]} (E_DFT={rows[imx][2]:.4f})")
    if out:
        with open(out, 'w') as f:
            f.write(f"# window [{emin},{emax}] eV: N={nmatch}, RMS={rms*1000:.3f} meV, MAX={mx*1000:.3f} meV\n")
            f.write("# ik  iband(DFT)  E_DFT(eV)  E_Wannier(eV)  dE(meV)\n")
            for r in rows:
                f.write(f"{r[0]:5d} {r[1]:5d} {r[2]:12.5f} {r[3]:12.5f} {r[4]*1000:10.3f}\n")

if __name__ == '__main__':
    main()
