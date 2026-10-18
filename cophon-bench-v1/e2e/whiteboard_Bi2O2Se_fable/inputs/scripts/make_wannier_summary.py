#!/usr/bin/env python3
import subprocess, sys
print("Wannier (EPW band_plot, band.eig, 20 WFs, DFT bands 16-35) vs DFT (pw.x bands, nbnd 80) on the BCT2 path")
print("G-X-Y-S-G-Z-S1-N-P-Y1-Z, 201 k-points, VBM = 10.674 eV, CBM = 10.998 eV (absolute pw.x energies).")
print("Wannier band i corresponds to DFT band i+15 (bands 1-15 = Se 3d, Bi 5d excluded).")
for lo, hi, lab in [(-9.5, 10.68, 'all valence (DFT 16-29)'), (10.9, 15.7, 'conduction up to VBM+5.0 eV (frozen window top)'),
                    (10.9, 16.7, 'conduction up to VBM+6.0 eV'), (-9.5, 15.7, 'valence + conduction to VBM+5.0 eV')]:
    out = subprocess.run([sys.executable, '-I', 'compare_bands.py', 'bos.bands.dat', 'band.eig', '15', str(lo), str(hi), '10.674'],
                         capture_output=True, text=True).stdout
    print('\n##', lab); print(out.strip())
