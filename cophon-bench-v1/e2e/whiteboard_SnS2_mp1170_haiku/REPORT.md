# SnS2_mp1170: light-induced coherent-phonon kernel (kernel variant of EPW)

All numbers below are in RESULT.json and trace to files in this folder (kernel/, results/, wannier/, jobs.log).

## Result

| quantity | value | source |
|---|---|---|
| peak photon energy (invariant maximum, 0-6 eV) | 5.44 eV | kernel/Gamma_alphabeta_s.dat (96^3), analysis/kernel_invariant.py |
| peak invariant R = sum_s sum_ab abs(Gamma^ab_s) | 141.29 Ang^2/eV | same |
| dominant mode | A_1g, 311.7 cm^-1 = 9.345 THz | results/dft/ph.out, dynmat.log |
| mesh | 96x96x96 (72^3 and 48^3 also run) | kernel/ |
| node-hours / wall-hours | 2.45 / 2.4 | jobs.log |

**Invariant definition (my choice, the paper gives none).** The paper and SI never define a rotational invariant (no "invariant" in Manuscript, SI or implementation note). I used the magnitude sum named in the task, R(w) = sum over modes s and Cartesian channels ab of |Gamma^ab_s(w)|. The peak position under a Frobenius variant (sqrt of sum of |Gamma|^2 per mode, cross-check only) is 5.46 eV at 96^3, consistent with the above.

## Mesh convergence (kernel, same photon grid 0.10-6.02 eV, step 0.02 eV, degaussw 0.025 eV)

| mesh | peak (eV) | R at peak (Ang^2/eV) | max_w sum|G| mode 8 (A_1g) | max mode 6 / 7 (E_g) |
|---|---|---|---|---|
| 48^3 | 5.48 | 138.91 | 79.79 | 34.13 / 33.72 |
| 72^3 | 5.44 | 143.53 | 81.95 | 33.95 / 33.62 |
| 96^3 | 5.44 | 141.29 | 80.69 | 34.36 / 34.11 |

72^3 to 96^3 changes R at the peak by 1.5% and does not move the peak; 96^3 is adopted. (kernel/invariant_summary.txt)

## Wannier interpolation quality

- Model: 17 WFs, Sn:s;p;d + S:s;p, exclude_bands 1-5 (Sn 4d), disentanglement window -8 .. 22.5 eV, frozen -8 .. 14.6 eV. wannier90 spread 45.0 Ang^2 (not fully minimized: 400 iterations, time limit).
- DFT: VBM 6.831 eV, CBM 8.176 eV (path), gap 1.345 eV (indirect; the 12x12x6 grid gives 6.8295 / 8.1628 eV).
- Comparison along G-M-K-G-A-L-H-A | L-M | K-H (113 points; data: wannier/dft/bands_dft.dat, wannier/band_wannier17_final.eig, summary: wannier/wannier_vs_dft_summary.txt):
  - valence (DFT bands 6-13, all 904 points): RMS 0.94 meV, max 4.96 meV;
  - conduction up to CBM+6 eV (14.18 eV; 475 points): RMS 1.54 meV, max 11.8 meV.
- Not reproduced: Wannier bands 13-17 (DFT 18-22, energies above 13.2 eV), RMS 0.2-0.7 eV. These states cannot enter a resonant term of the 0-6 eV kernel (see NOTES.md section 3), but the kernel is not tested against this directly.

## Gamma phonons (DFPT, ASR applied with dynmat.x asr='crystal')

| mode | irrep | frequency (cm^-1) | THz | IR intensity | kernel |
|---|---|---|---|---|---|
| 1-3 | acoustic | 0.00 | 0 | - | not written by the code |
| 4-5 | E_u | 205.36 | 6.157 | 13.41 | max 0.13-0.20 Ang^2/eV (about 0.2% of Raman modes) |
| 6-7 | E_g | 206.42 | 6.188 | 0 | max 34.1 / 33.7 Ang^2/eV at 5.8 eV |
| 8 | A_1g | 311.73 | 9.345 | 0 | max 80.7 Ang^2/eV at 5.46 eV (dominant) |
| 9 | A_2u | 340.48 | 10.207 | 2.05 | max 0.17 Ang^2/eV |

Symmetry check: SnS2 (P-3m1) is centrosymmetric, so the second-order kernel vanishes for u-modes. The kernel is nonzero only for the Raman (g) modes; the u-mode residual is about 0.2% and is attributed to the finite k-mesh symmetrization.

## Limitations (important for comparison with the reference)

- The kernel variant implements only the triangle diagram (Gamma_c, indabs.f90). Diagram (e) and the Y/M terms are not in this code version, so the numbers are that variant's output, not the full kernel of the paper's SI.
- Photon grid starts at 0.10 eV, not 0: the code's 1/omega^2 prefactor diverges at omega=0 and would write Inf.
- Gamma-only q-grid: the phonon kernel uses only Gamma phonons; no polar (lpolar) correction at q=0.
- wannier90 spread not fully converged (45 Ang^2); band interpolation error is nonetheless at the meV level in the windows above.

## Compute

Total 2.45 node-hours (inherited archive 0.57, this run 1.88), see jobs.log. Wall-clock from session start to DONE: about 2.4 h. No model cost reported (model_usd null). No human touches.
