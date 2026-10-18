"""DFT (pw.x bands) vs Wannier-interpolated bands along the path G-X-M-G-R.

inputs: dft_bands.out (pw.x 'bands' stdout, 30 bands), knbo3_band.dat (wannier90 gnuplot: blocks of 'x E' per band,
        separated by blank lines), and the Wannier abscissa x from the same path convention.
DFT abscissa is built from the crystal k-points in the output using the reciprocal vectors of the sealed cell.
Compares sorted energies of Wannier band n with DFT band (n + 11) (1-based: DFT bands 12..25 = 14 WF manifold)
and reports RMS and max |dE| (meV) over
  valence window : DFT bands 12..20 (O 2p manifold), all k
  conduction     : DFT bands 21..25 with E <= CBM + 6 eV (CBM = 10.6173 eV on the 6x6x6 NSCF grid)
usage: python3 -I band_compare.py dft_bands.out knbo3_band.dat
"""
import sys, math, json

A = [(-0.0, 3.26699347, 2.31667251), (2.82929933, -1.63349673, 2.31667251), (-2.82929933, -1.63349673, 2.31667251)]

def dot(u, v): return sum(a * b for a, b in zip(u, v))
def cross(u, v): return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
V = dot(A[0], cross(A[1], A[2]))
B = [tuple(2*math.pi*x/V for x in cross(A[(i+1) % 3], A[(i+2) % 3])) for i in range(3)]

def parse_dft(path):
    ks, eigs = [], []
    lines = open(path).read().splitlines()
    i = 0
    while i < len(lines):
        s = lines[i]
        if 'bands (ev)' in s:
            kc = [float(x) for x in s.split('k =')[1].split('(')[0].replace('-', ' -').split()]
            vals = []
            i += 1
            while len(vals) < 30 and i < len(lines):
                t = lines[i].split()
                try:
                    vals += [float(x) for x in t]
                except ValueError:
                    break
                i += 1
            ks.append(kc); eigs.append(vals[:30])
        i += 1
    return ks, eigs

def kdist_cart(kcart):
    # cumulative path length from the pw.x Cartesian k (2pi/alat units); rescaled to Wannier90 later
    x = [0.0]
    for n in range(1, len(kcart)):
        d = [kcart[n][c]-kcart[n-1][c] for c in range(3)]
        x.append(x[-1] + math.sqrt(dot(d, d)))
    return x

def parse_wan(path):
    blocks, cur = [], []
    for line in open(path):
        s = line.split()
        if not s:
            if cur: blocks.append(cur); cur = []
            continue
        cur.append((float(s[0]), float(s[1])))
    if cur: blocks.append(cur)
    return blocks

def interp(xs, ys, x):
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    lo, hi = 0, len(xs)-1
    while hi - lo > 1:
        mid = (lo+hi)//2
        if xs[mid] <= x: lo = mid
        else: hi = mid
    t = (x-xs[lo])/(xs[hi]-xs[lo]) if xs[hi] != xs[lo] else 0.0
    return ys[lo]*(1-t)+ys[hi]*t

if __name__ == '__main__':
    kcrys_all, eigs = parse_dft(sys.argv[1])
    wan = parse_wan(sys.argv[2])
    xraw = kdist_cart(kcrys_all)
    scale = wan[0][-1][0] / xraw[-1]
    xd = [x*scale for x in xraw]
    CBM = 10.6173
    res = {'n_dft_k': len(xd), 'n_wan_blocks': len(wan)}
    # Wannier band block w (0..13) -> DFT band index 11+w (0-based), i.e. DFT bands 12..25 (1-based)
    val_err, cond_err = [], []
    per_band = {}
    for w, blk in enumerate(wan):
        xw = [p[0] for p in blk]; yw = [p[1] for p in blk]
        ib = 11 + w
        errs = []
        for n, xk in enumerate(xd):
            ed = eigs[n][ib]
            ew = interp(xw, yw, xk)
            errs.append((ew-ed)*1000.0)   # meV
        if ib <= 19:
            val_err += errs
        elif all(e <= CBM+6.0 for e in [eigs[n][ib] for n in range(len(xd))]) or True:
            sel = [errs[n] for n in range(len(xd)) if eigs[n][ib] <= CBM+6.0]
            cond_err += sel
        per_band[ib+1] = {'rms_meV': math.sqrt(sum(e*e for e in errs)/len(errs)), 'max_abs_meV': max(abs(e) for e in errs)}
    def stats(v):
        if not v: return None
        return {'n': len(v), 'rms_meV': math.sqrt(sum(e*e for e in v)/len(v)), 'max_abs_meV': max(abs(e) for e in v)}
    res['valence_O2p_bands_12_20'] = stats(val_err)
    res['conduction_bands_21_25_upto_CBM+6eV'] = stats(cond_err)
    res['per_band'] = per_band
    print(json.dumps(res, indent=1))
