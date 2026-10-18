# Wannier-vs-DFT band comparison along the 131-point path (crystal coords, primitive reciprocal basis).
# Wannier H(k) from wannier90 nbfesb_hr.dat (eV), eigenvalues vs DFT path bands from the bands-run XML (eV).
import math, xml.etree.ElementTree as ET
import numpy as np
HA = 27.211386245988
LOG = '/home/wb/work/logs/bands/'

def read_hr(fn):
    with open(fn) as f:
        lines = f.readlines()
    nw, nr = int(lines[1]), int(lines[2])
    nd = math.ceil(nr / 15)
    deg = []
    for l in lines[3:3+nd]:
        deg += [int(x) for x in l.split()]
    body = [l.split() for l in lines[3+nd:] if len(l.split()) >= 7]
    assert len(body) == nr*nw*nw, (len(body), nr*nw*nw)
    Rs = np.zeros((nr, 3)); Hs = np.zeros((nr, nw, nw), dtype=complex)
    for n in range(nr):
        blk = body[n*nw*nw:(n+1)*nw*nw]
        Rs[n] = [int(blk[0][0]), int(blk[0][1]), int(blk[0][2])]
        for p in blk:
            i, j = int(p[3])-1, int(p[4])-1
            Hs[n, i, j] = complex(float(p[5]), float(p[6]))
        Hs[n] /= deg[n]
    return nw, Rs, Hs

nw, Rs, Hs = read_hr(LOG + 'nbfesb_hr.dat')
hs = [(0,0,0),(0.5,0,0.5),(0.5,0.25,0.75),(0.5,0.5,0.5),(0,0,0),(0.375,0.375,0.75)]
npts = [30, 20, 20, 30, 30]
kp = []
for i in range(5):
    a, b = np.array(hs[i]), np.array(hs[i+1])
    for j in range(npts[i]):
        kp.append(a + j/npts[i]*(b - a))
kp.append(np.array(hs[-1]))
kp = np.array(kp)

root = ET.parse(LOG + 'dft_path_data-file-schema.xml').getroot()
dft = np.array([[float(x)*HA for x in ks.find('eigenvalues').text.split()] for ks in root.iter('ks_energies')])
assert dft.shape[0] == len(kp), (dft.shape, len(kp))

# Wannier eigenvalues: H(k) = sum_R H(R) exp(i 2pi k.R)
ph = np.exp(2j*np.pi*kp @ Rs.T)                # (nk, nR)
Hk = np.einsum('kr,rij->kij', ph, Hs)
wan = np.linalg.eigvalsh(Hk)                    # (nk, nw) sorted ascending

# DFT bands 14..29 (1-based), i.e. the 16 bands of the Wannier window
dft16 = dft[:, 13:13+nw]
VBM, CBM = 16.9722, 17.5049
err = wan - dft16
def stats(mask):
    e = err[mask]
    return math.sqrt(np.mean(e**2)*1000)*1, np.max(np.abs(e))*1000
# valence: DFT bands 14..22 (indices 13..21) ; conduction within CBM+6 eV: bands 23.. up to energy CBM+6
val_idx = list(range(0, 9))                     # bands 14..22
cond_mask_e = (dft16 > CBM - 1e-6) & (dft16 <= CBM + 6.0)
val_mask = np.zeros_like(err, dtype=bool); val_mask[:, val_idx] = True
rms_v = math.sqrt(np.mean(err[:, val_idx]**2))*1000
max_v = np.max(np.abs(err[:, val_idx]))*1000
rms_c = math.sqrt(np.mean(err[cond_mask_e]**2))*1000
max_c = np.max(np.abs(err[cond_mask_e]))*1000
print('path points', len(kp), 'num_wann', nw, 'R vectors', len(Rs))
print('valence (DFT bands 14-22, all path k): RMS = %.2f meV, max = %.2f meV' % (rms_v, max_v))
print('conduction (CBM..CBM+6 eV, sorted-window matched): RMS = %.2f meV, max = %.2f meV, n = %d' % (rms_c, max_c, cond_mask_e.sum()))
print('DFT valence max', round(dft[:, 21].max(), 4), 'min band 14 =', round(dft[:, 13].min(), 4))
print('Wannier band 14..22 at Gamma:', np.round(wan[0, :9], 3))
print('DFT band 14..22 at Gamma:  ', np.round(dft[0, 13:22], 3))
print('per-band RMS (meV) and max (meV), bands 14..29:')
for b in range(16):
    e = err[:, b]*1000
    kmax = int(np.argmax(np.abs(e)))
    print(14+b, round(math.sqrt(np.mean(e**2)), 1), round(float(np.max(np.abs(e))), 1), 'at path idx', kmax, 'dft %.3f wan %.3f' % (dft16[kmax, b], wan[kmax, b]))
# write the comparison data used in REPORT.md
with open(LOG + 'band_compare_path.csv', 'w') as f:
    f.write('idx,kx,ky,kz,' + ','.join('dft_b%d' % b for b in range(14, 14+nw)) + ',' + ','.join('wan_b%d' % b for b in range(14, 14+nw)) + '\n')
    for i in range(len(kp)):
        f.write('%d,%.6f,%.6f,%.6f,' % (i, kp[i][0], kp[i][1], kp[i][2]) + ','.join('%.5f' % x for x in dft16[i]) + ',' + ','.join('%.5f' % x for x in wan[i]) + '\n')
with open(LOG + 'band_compare_summary.txt', 'w') as f:
    f.write('Wannier (wannier90 nbfesb_hr.dat, 8x8x8 coarse, 22 WF) vs DFT (PBE, 90 Ry, path 131 k-points)\n')
    f.write('valence bands 14-22 (all path k): RMS %.2f meV, max %.2f meV\n' % (rms_v, max_v))
    f.write('conduction states with DFT energy in [CBM, CBM+6 eV] (CBM=17.505 eV): RMS %.2f meV, max %.2f meV, n=%d\n' % (rms_c, max_c, int(cond_mask_e.sum())))
