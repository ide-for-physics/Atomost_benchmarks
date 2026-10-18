# Wannier (wannier90 restart=plot) vs DFT (pw.x bands) along the Gamma-X-W-K-Gamma-L path.
# Both mapped onto a common arc length in Cartesian k (2pi/alat units, reciprocal basis from the pw.x output).
# Wannier band i (1..8) is compared with DFT band 5+i (DFT bands 6..13 = 4 valence + 4 conduction bands of the 15-band window).
import re, sys
import numpy as np
dft_path, wan_dat, wan_kpt = sys.argv[1], sys.argv[2], sys.argv[3]
txt = open(dft_path).read()
b = []
for ln in txt.splitlines():
    m = re.match(r'\s*b\((\d)\) = \(\s*([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)\s*\)', ln)
    if m and len(b) < 3:
        b.append([float(m.group(2)), float(m.group(3)), float(m.group(4))])
B = np.array(b)  # rows b1,b2,b3 in 2pi/alat
# DFT k-points and eigenvalues
kc, eig = [], []
lines = txt.splitlines()
i = 0
while i < len(lines):
    if 'bands (ev)' in lines[i] and lines[i].strip().startswith('k ='):
        m = re.search(r'k =(.*?)\(', lines[i])
        nums = re.findall(r'-?\d+\.\d+', m.group(1))
        nums = [float(x) for x in nums[:3]]
        vals = []
        j = i + 1
        while len(vals) < 20:
            vals += [float(x) for x in re.findall(r'-?\d+\.\d+', lines[j])]
            j += 1
        kc.append(nums); eig.append(vals[:20])
        i = j
    else:
        i += 1
kc = np.array(kc); eig = np.array(eig)
kcart_dft = kc                      # already cartesian in 2pi/alat
# Wannier crystal k-points -> cartesian (2pi/alat): k = sum_i c_i b_i
kcr = np.loadtxt(wan_kpt, skiprows=1, usecols=(0, 1, 2))
# first line of gap_band.kpt is the count
kcart_wan = kcr @ B
wd = np.loadtxt(wan_dat)
nk_w = len(kcr)
# gap_band.dat: blocks per band, nk_w rows each (whitespace separated: x, E)
E_w = wd[:, 1].reshape(-1, nk_w)[:8]   # 8 bands x nk_w
def arc(kpts):
    d = np.zeros(len(kpts))
    d[1:] = np.cumsum(np.linalg.norm(np.diff(kpts, axis=0), axis=1))
    return d
s_dft = arc(kcart_dft); s_wan = arc(kcart_wan)
# normalise both to unit length so the two parametrisations are comparable
s_dft_n = s_dft / s_dft[-1]; s_wan_n = s_wan / s_wan[-1]
print('DFT points: %d, Wannier points: %d' % (len(kcart_dft), nk_w))
VBM = 7.6383   # eV (QE absolute, from pw.x highest occupied level)
CBM = 9.2802   # eV (QE absolute, NSCF lowest unoccupied level)
res = {'valence': [], 'conduction': []}
for iw in range(8):
    dft_b = eig[:, 5 + iw]
    wan_i = np.interp(s_dft_n, s_wan_n, E_w[iw])
    diff = wan_i - dft_b
    kind = 'valence' if iw < 4 else 'conduction'
    if kind == 'conduction':
        mask = dft_b <= CBM + 6.0
    else:
        mask = dft_b > -30.0
    res[kind].append((iw + 1, 5 + iw + 1, np.sqrt(np.mean(diff[mask] ** 2)), np.max(np.abs(diff[mask])), mask.sum()))
for kind in res:
    for wi, di, rms, mx, n in res[kind]:
        print('%-11s Wannier band %d vs DFT band %2d : RMS %.4f eV (%.1f meV), max %.4f eV (%.1f meV), n=%d'
              % (kind, wi, di, rms, rms * 1000, mx, mx * 1000, n))
allv = np.concatenate([np.array([r[2] for r in res['valence']]), np.array([r[2] for r in res['conduction']])])
print('band-averaged RMS over 8 bands: %.1f meV' % (np.mean(allv) * 1000))
