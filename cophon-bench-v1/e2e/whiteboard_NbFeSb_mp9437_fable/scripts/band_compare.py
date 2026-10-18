#!/usr/bin/env python3
"""Compare DFT bands (parsed pw.x bands, nk x nbnd eV) with EPW band.eig (Wannier) on the same k path.
Usage: band_compare.py dft_bands.dat band.eig nexclude evbm ecbm [emax_above_cbm=6]
Only Wannier bands that are inside the frozen window are compared band-by-band (index-matched after
skipping nexclude DFT bands); windows: valence (E<=VBM) and conduction (VBM<E<=CBM+emax).
"""
import sys, numpy as np
dft = np.loadtxt(sys.argv[1])
nex = int(sys.argv[3]); evbm = float(sys.argv[4]); ecbm = float(sys.argv[5])
emax = ecbm + (float(sys.argv[6]) if len(sys.argv) > 6 else 6.0)
lines = [l for l in open(sys.argv[2]) if l.strip() and '&plot' not in l]
ks = np.array([[float(x) for x in lines[i].split()] for i in range(0, len(lines), 2)])
wan = np.array([[float(x) for x in lines[i].split()] for i in range(1, len(lines), 2)])
nk, nb = wan.shape
assert nk == dft.shape[0], (nk, dft.shape)
d = dft[:, nex:nex+nb]
diff = wan - d
mask_v = d <= evbm + 1e-3
mask_c = (d > evbm + 1e-3) & (d <= emax)
print(f"# {nk} k-points, {nb} Wannier bands vs DFT bands {nex+1}..{nex+nb}")
for name, mask in [('valence (E<=VBM)', mask_v), (f'conduction (CBM..CBM+{emax-ecbm:.1f} eV)', mask_c), ('both windows', mask_v | mask_c)]:
    x = diff[mask]
    print(f"{name:36s} N={x.size:5d}  RMS = {np.sqrt(np.mean(x**2))*1000:7.2f} meV   max|dE| = {np.abs(x).max()*1000:7.2f} meV")
# per-band summary
print("# band  DFTmin  DFTmax  RMS(meV) max(meV)")
for ib in range(nb):
    print(f"{nex+ib+1:4d} {d[:,ib].min():8.3f} {d[:,ib].max():8.3f} {np.sqrt(np.mean(diff[:,ib]**2))*1000:9.2f} {np.abs(diff[:,ib]).max()*1000:9.2f}")
np.savetxt('wannier/band_diff_meV.dat', diff*1000, fmt='%9.3f', header='Wannier - DFT (meV), rows = k along path, cols = bands')
np.savetxt('wannier/wannier_bands_path.dat', wan, fmt='%10.4f', header='EPW Wannier-interpolated bands (eV) on the DFT path')
