#!/usr/bin/env python3
"""Compare DFT bands (pw.x bands.out, verbosity high) with Wannier-interpolated bands (wannier90 kno_band.dat)
along the same k-path. Both are on the same path with the same number of points per segment only if
bands_num_points matches; here we interpolate the Wannier bands onto the DFT k-distance grid.
Usage: compare_bands.py bands.out kno_band.dat kno_band.kpt efermi_or_vbm nexclude
Reports RMS and max |E_DFT - E_W90| for valence bands (O 2p manifold) and conduction bands up to CBM+6 eV.
"""
import sys, re
import numpy as np

bands_out, wband, wkpt = sys.argv[1], sys.argv[2], sys.argv[3]
vbm = float(sys.argv[4]); nexcl = int(sys.argv[5])
cbm = float(sys.argv[6]) if len(sys.argv) > 6 else None

# ---- DFT bands: parse k-points (cart, 2pi/alat) and eigenvalues
txt = open(bands_out).read()
alat = float(re.search(r"lattice parameter \(alat\)\s*=\s*([\d.]+)", txt).group(1))
nb = int(re.search(r"number of Kohn-Sham states=\s*(\d+)", txt).group(1))
blocks = re.findall(r"k =(.{21})\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s*\n(.*?)(?=\n\s*occupation numbers|\n\s*k =|\n\s*highest|\n\s*Writing)", txt, re.S)
ks, es = [], []
for kstr, body in blocks:
    vals = [float(x) for x in re.findall(r"-?\d+\.\d+", body)]
    if len(vals) < nb:
        continue
    ks.append([float(x) for x in re.findall(r"-?\d+\.\d+", kstr)]); es.append(vals[:nb])
ks = np.array(ks); es = np.array(es)
nkeep = int(sys.argv[7]) if len(sys.argv) > 7 else len(ks)   # DFT path may contain an extra trailing segment
ks = ks[:nkeep]; es = es[:nkeep]
dk = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ks, axis=0), axis=1))]  # 2pi/alat units
print(f"DFT: {len(ks)} k-points, {nb} bands, path length {dk[-1]:.4f} (2pi/alat)")

# ---- Wannier bands (gnuplot format: x E, blank line between bands)
wb = [[]]
for line in open(wband):
    if line.strip() == "":
        if wb[-1]: wb.append([])
        continue
    x, e = line.split()[:2]
    wb[-1].append((float(x), float(e)))
wb = [np.array(b) for b in wb if len(b)]
nw = len(wb); xw = wb[0][:, 0]
ew = np.array([b[:, 1] for b in wb]).T  # (nk_w, nw)
print(f"W90: {ew.shape[0]} k-points, {nw} bands, path length {xw[-1]:.4f} (1/Ang)")
# rescale Wannier x (1/Ang) to DFT path length (2pi/alat units)
xw_s = xw / xw[-1] * dk[-1]
ewi = np.array([np.interp(dk, xw_s, ew[:, i]) for i in range(nw)]).T  # (nk_dft, nw)

# ---- compare: DFT bands nexcl+1 .. nexcl+nw vs Wannier bands (sorted at each k)
ed = es[:, nexcl:nexcl + nw]
diff = ed - np.sort(ewi, axis=1)
# masks
val = ed <= vbm + 1e-3
if cbm is None:
    cbm = ed[ed > vbm + 0.5].min()
cond = (ed > vbm + 1e-3) & (ed <= cbm + 6.0)
def stats(m, label):
    d = np.abs(diff[m])
    print(f"{label}: n={d.size}  RMS = {np.sqrt((d**2).mean())*1000:.2f} meV   max = {d.max()*1000:.2f} meV")
stats(val, "valence (O 2p manifold, 9 bands)")
stats(cond, f"conduction up to CBM+6 eV (CBM={cbm:.3f})")
stats((ed > vbm + 1e-3) & (ed <= cbm + 4.0), "conduction up to CBM+4 eV")
stats((ed > vbm + 1e-3) & (ed <= cbm + 3.0), "conduction up to CBM+3 eV")
# per-band max
for i in range(nw):
    d = np.abs(diff[:, i]); print(f"  band {nexcl+1+i:3d}: Emin {ed[:,i].min():8.3f} Emax {ed[:,i].max():8.3f}  RMS {np.sqrt((d**2).mean())*1000:7.2f} meV  max {d.max()*1000:7.2f} meV")
np.savetxt("bands_compare.dat", np.c_[dk, ed, np.sort(ewi, axis=1)],
           header=f"k-distance(2pi/alat)  DFT bands {nexcl+1}-{nexcl+nw} (eV)  |  Wannier bands 1-{nw} (eV)", fmt="%.6f")
print("wrote bands_compare.dat")
