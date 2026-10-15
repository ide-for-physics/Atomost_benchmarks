#!/usr/bin/env python3
"""Compare kernel invariants across fine k-meshes.
Usage: mesh_convergence.py label1:Gamma_file1 label2:Gamma_file2 ...
Prints, per mesh: peak photon energy and S1 of the global maximum, triplet sums at the peak, and the relative RMS
difference of the total S1 spectrum (sum over modes, 1-6 eV) with respect to the last (densest) mesh.
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kernel_invariants import parse, invariants

def spectra(fn):
    order, modes = parse(fn)
    om = modes[order[0]]['omega']
    S1 = {im: [invariants(G)[0] for G in modes[im]['G']] for im in order}
    F = {im: [invariants(G)[1] for G in modes[im]['G']] for im in order}
    tot = [sum(S1[im][i] for im in order) for i in range(len(om))]
    return order, modes, om, S1, F, tot

def main():
    runs = [(a.split(':')[0], a.split(':', 1)[1]) for a in sys.argv[1:]]
    data = [(lab,) + spectra(fn) for lab, fn in runs]
    ref = data[-1]
    print("# mesh | omega_peak(total S1) | total S1 at peak | triplet sums S1 (modes 4-6 | 7-9) at peak | per-mode peak S1 (4..9) | per-mode F at peak | relRMS(total S1 vs densest, 1-6 eV)")
    for lab, order, modes, om, S1, F, tot in data:
        ipk = max(range(len(om)), key=lambda i: tot[i])
        t46 = sum(S1[im][ipk] for im in order if im <= 6); t79 = sum(S1[im][ipk] for im in order if im >= 7)
        permode = ' '.join(f"{S1[im][ipk]:7.3f}" for im in order)
        perF = ' '.join(f"{F[im][ipk]:7.3f}" for im in order)
        idx = [i for i, w in enumerate(om) if 1.0 <= w <= 6.0]
        num = sum((tot[i] - ref[6][i]) ** 2 for i in idx); den = sum(ref[6][i] ** 2 for i in idx)
        rel = math.sqrt(num / den) if den > 0 else float('nan')
        print(f"{lab:8s} {om[ipk]:7.3f} eV  {tot[ipk]:9.3f}  | {t46:8.3f} | {t79:8.3f} | {permode} | {perF} | {rel*100:6.2f} %")
    # per-mode peak energies
    print("# per-mode peak photon energy (eV) of S1_s:")
    for lab, order, modes, om, S1, F, tot in data:
        print(f"{lab:8s} " + ' '.join(f"{om[max(range(len(om)), key=lambda i: S1[im][i])]:6.3f}" for im in order))

if __name__ == '__main__':
    main()
