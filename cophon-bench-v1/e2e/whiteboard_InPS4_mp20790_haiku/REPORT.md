# REPORT: light-induced coherent-phonon generation kernel, InPS4_mp20790

Numbers below are the same as RESULT.json.

| key | value |
|---|---|
| kernel_file | kernel/Gamma_alphabeta_s.dat (72x72x72 fine k-mesh, converged) |
| peak_ev | 3.05 eV (grid step 0.05 eV, range 0-6 eV) |
| peak_a2_per_ev | 266.24 A^2/eV (total invariant at the peak, see definition) |
| mode_thz | 7.8734 THz (262.63 cm^-1, file mode 11) |
| mode_irrep | A (S4 eigenvalue +1, C2 eigenvalue +1) |
| mesh | 72x72x72 |
| node_hours | 5.41 (jobs.log) |
| wall_hours | 5.03 at DONE |

## 1. Scope, and what the code actually computes (read first)
- The authors' EPW "kernel variant" (EPW/src/indabs.f90 in the toolchain, read-only) implements only the
  triangle diagram Gamma_c plus Pi_0 ("v1 scope"). Diagram (e) of SI Eq. (Gamma^{ab}_s, diagram e) is NOT in the code.
  The kernel file therefore is the triangle-diagram kernel, not the full kernel of the paper. The comparison with a
  reference must take this into account.
- Output: Gamma_alphabeta_s.dat, nine Cartesian channels xx,yy,zz,xy,xz,yz,yx,zx,zy (the header line lists six) as (Re, Im) in A^2/eV, for each
  Gamma mode with frequency in meV in the header. Energy 0 gives NaN (EPW divides by the photon energy squared); the NaN row is not used.

## 2. Cell and structure
- Cell: structure.cif / structure_POSCAR exactly as given (sealed, not relaxed). Volume 143.60 A^3.
- Forces after SCF: max 3.4e-5 Ry/bohr, so no internal relaxation was needed (positions as given).
- Pressure of the sealed cell: 18.9 kbar (reported, not acted on).
- Point group from QE: 4 operations (E, C2z, S4, S4^3), i.e. S4, non-centrosymmetric.
- Electronic gap: VBM 4.5773 eV (indirect, off Gamma), CBM 6.8554 eV (Gamma), indirect gap 2.278 eV.

## 3. DFT setup
- pw.x, PBE, PseudoDojo NC FR v0.4 standard (In, P, S), scalar-relativistic use (no spin-orbit).
- ecutwfc 80 Ry, ecutrho 320 Ry (In "high" hint 82 Ry), 42 valence electrons, 40 bands, fixed occupations.
- SCF 6x6x6 Gamma-centred (converged to 1e-12 Ry, 12 iterations). NSCF on the explicit full 6x6x6 list (216 points, nosym).

## 4. DFPT phonons at Gamma (ph.x, dynmat.x with asr='crystal')
- ph.x ldisp 3x3x3, tr2_ph 1e-16, six irreducible q; wall time 2 h 23 min on one node.
- Gamma frequencies after the acoustic sum rule (cm^-1; irrep from S4 projection of each eigenvector):

| file mode | cm^-1 | THz | IR | irrep |
|---|---|---|---|---|
| 1-3 | 0 (acoustic) | 0 | - | - |
| 4,5 | 83.89 | 2.515 | 0.591 | E |
| 6 | 109.93 | 3.296 | 3.207 | B |
| 7 | 147.55 | 4.423 | 0.000 | A |
| 8,9 | 169.48 | 5.081 | 0.951 | E |
| 10 | 244.90 | 7.342 | 0.139 | B |
| 11 | 262.63 | 7.873 | 0.000 | A |
| 12 | 310.61 | 9.312 | 3.486 | B |
| 13,14 | 319.10 | 9.567 | 3.944 | E |
| 15 | 398.80 | 11.956 | 0.000 | A |
| 16 | 500.38 | 15.001 | 11.010 | B |
| 17,18 | 537.65 | 16.118 | 9.840 | E |

- Irreps: the non-degenerate modes are A (S4 = +1) or B (S4 = -1), from the eigenvalue of the S4 operation on each
  mass-weighted eigenvector; the degenerate pairs give mixed values, consistent with E. Counts: A 3, B 4, E 8 pairs.

## 5. Mesh convergence of the kernel (Gamma-only fine q, coarse k 6x6x6)
- Invariant I(w) = sum over modes s and Cartesian channels ab of |Gamma^{ab}_s(w)| (complex magnitude), in A^2/eV.
- Peak of total I(w) over 0 < w <= 6 eV:

| fine mesh | peak (eV) | I at peak (A^2/eV) | dominant mode at peak |
|---|---|---|---|
| 48^3 | 3.05 | 267.17 | file 11, 32.55 meV (A), 110.4 |
| 72^3 | 3.05 | 266.24 | file 11, 32.55 meV (A), 109.8 |
| 96^3 | - | - | not obtained: 96^3 ran out of memory on one node (128 ranks), and 72^3 also OOM on one node; 72^3 was then run on two nodes with 256 pools |

- 48 to 72 changes the peak value by 0.35% and does not move the peak energy or the dominant mode, so the adopted
  mesh is 72^3. A 96^3 check was not completed (memory); this is a stated limitation.
- The two-node 72^3 run completed in 51 min; the 96^3 run was not repeated on two nodes because the budget and time were better spent on the Wannier fit checks.

## 6. Wannier interpolation quality (24 Wannier functions)
- Projections: In s,p; P s,p; S s,p (24 orbitals), nbndsub = 24, from 40 DFT bands.
- Disentanglement window -4.5..15.0 eV, frozen window -1.0..12.9 eV. Frozen states per k are at most 22 < 24.
- Comparison: pw.x bands along an 83-point path (path_crystal.txt, zone-face/zone-centre points of the primitive
  reciprocal lattice; not the textbook BCT path) against Fourier interpolation of EPW's inps4_hr.dat (numpy, bands/band_check.py).
- Relevant window: from VBM-6 eV to CBM+6 eV (-1.42..12.86 eV). 81 of 83 k-points have equal DFT and Wannier
  state counts in this window and are used.

| band set | n | RMS (eV) | max (eV) |
|---|---|---|---|
| valence (up to VBM) | 871 | 0.0015 | 0.0079 |
| conduction (from CBM) | 803 | 0.0090 | 0.0647 |

- The largest conduction error (0.065 eV) sits at 12.3-12.8 eV, at the upper edge of the frozen window.
- Iteration history: with the frozen window ending at 8 eV the relevant-window RMS was 44 meV and max 271 meV. Widening the frozen window to 12.9 eV reduced it to 6.4 meV RMS (max 65 meV). The 6.4 meV figure is the one reported.
- The EPW band_plot option did not write band.eig in this configuration, so the comparison uses my own interpolation.
- Data: bands/dft_path_eigs_eV.txt, bands/wannier_path_eigs_eV.txt, bands/path_points_crystal.txt.

## 7. Electron-phonon and kernel inputs
- EPW: elph, wannierize (internal), nbndsub 24, nk 6x6x6, nq 1x1x1 (Gamma only), nqf 1x1x1, nkf = mesh,
  efermi_read with mid-gap Ef = 5.7164 eV, degaussw 0.025 eV (paper value), lindabs, omegamin 0, omegamax 6 eV, omegastep 0.05 eV
  (121 photon points), ladsmear false, eps_acoustic default (0.1 cm^-1).
- The 3x3x3 DFPT data were computed but could not be used by EPW: with the full q-grid, EPW reported "wrong qpoint"
  at irreducible q #3 (its q-star ordering differs from ph.x's). For the Gamma-only kernel only the Gamma dynamical matrix
  and the Gamma dvscf are needed, and the coarse k-mesh still drives the Wannier interpolation. This is a deliberate reduction,
  stated here.
- dyn and dvscf names: EPW expects tmp/_ph0/<prefix>.dyn_q<N> and <prefix>.dvscf_q<N>; these were copied/linked from the ph.x output.

## 8. Kernel peaks (72^3, adopted)
- Total invariant: 3.00 eV 191.9; 3.05 eV 266.2 (peak); 3.10 eV 260.0 A^2/eV.
- Per-mode maxima (file mode, meV, peak energy, value): 7 (18.29 meV, A, 3.05 eV, 84.1); 11 (32.55 meV, A, 3.10 eV, 114.8);
  15 (49.44 meV, A, 5.25 eV, 66.3); 5 (10.38, 3.30 eV, 11.4); 6 (13.62, 5.50 eV, 10.5); 16 (62.04, 5.25 eV, 10.9); others < 12.
- Peak_a2_per_ev is the total invariant at the peak (266.24). The dominant-mode value at 3.05 eV is 109.8 A^2/eV.

## 9. Compute used
- jobs.log: 18 Slurm jobs of this project, total 5.41 node-hours (sum nodes x elapsed). The failed attempts (launch and EPW
  configuration errors, two out-of-memory runs) are included and marked.
- Wall time from start to DONE: 5.03 h. Queue wait for `small` was short; the phonon job ran 2 h 23 min.
- Jobs from other users in the same login account (names cds_*, knbo_*) were not touched and are not counted.

## 10. Limitations
1. Triangle diagram only (see Section 1). The paper's full kernel also has diagram (e), which is absent from this code.
2. Coarse q-grid for EPW reduced to Gamma (Section 7).
3. 96^3 not converged (memory); convergence is shown between 48^3 and 72^3 only.
4. Band-structure comparison used the path of Section 6 (not the textbook BCT path); EPW band_plot did not write its output.
5. Sealed cell with 18.9 kbar residual pressure, positions not relaxed beyond zero forces.
