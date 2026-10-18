# Bi2O2Se: light-induced coherent-phonon kernel (EPW kernel variant)

## Result (also in RESULT.json)
- Largest rotational invariant of the kernel on 0-6 eV, I_s(w) = sum over 9 Cartesian channels of |Gamma^ab_s(w)| (Å²/eV), at the adopted mesh 64x64x64:
  **peak at 3.80 eV, I = 40.11 Å²/eV, mode 9 (19.36 meV = 156.2 cm⁻¹ = 4.68 THz), irrep A1g** (ph.x label "A_1g X_1 M_1 R").
- Symmetry check: the mode-9 kernel is diagonal with xx = yy = 17.5, zz = 5.0, off-diagonals ~0 — the A1g form.
- Frobenius-norm alternative (sqrt sum |Gamma|²) gives the same mode and energy: 3.80 eV, F = 25.3 Å²/eV.
- **Convergence is NOT fully established** (see mesh table). The peak energy and mode agree between 48³ and 64³; the magnitude
  changes by 4.4% from 48³ to 64³. A third mesh (80³) was queued but cancelled (never started). The reported 64³ value is the finest
  mesh completed; treat ±5% as the present uncertainty.

## Cell and structure
- Sealed cell from structure.cif / structure_POSCAR, used exactly (no vc-relax). Volume 95.8 Å³.
- Internal coordinates relaxed at fixed cell (bfgs, 8x8x8, 90 Ry): converged in 1 BFGS step, displacement < 1e-4 crystal.
  Relaxed crystal positions: Bi 0.3531302 0.3531302 0; Bi 0.6468698 0.6468698 0; Se 0 0 0; O 0.25 0.75 0.5; O 0.75 0.25 0.5.
- Gap (PBE, fixed occupations, 8x8x8): VBM 10.669 eV, CBM 10.998 eV, gap 0.33 eV (absolute QE energies).

## Calculation setup (all inputs in inputs/, run-time files in run/, phrun/, fin*/, wv*/ on LUMI)
- PseudoDojo FR ONCV v0.4 standard (Bi, Se, O), scalar-relativistic use (no SOC). ecutwfc 90 Ry, ecutrho 360 Ry.
- SCF 8x8x8; NSCF on the explicit full 8x8x8 list (512 k), 44 bands.
- DFPT at Gamma (ph.x, tr2_ph 1e-13) from a fresh SCF on the 8x8x8 grid (59 irreducible k), epsil off (centrosymmetric cell).
- Wannier: EPW internal Wannier90 (18 WF: Bi s,p; Se s,p; O p; 8x8x8 coarse grid), disentanglement windows (absolute eV):
  outer [VBM-11, VBM+10]; frozen [VBM-6, VBM+5.5] (variant wv5, adopted, see below).
- EPW kernel: lindabs, degaussw 0.025 eV (SI electronic broadening), fsthick 9 eV, temperature 300 K (only used for the
  fixed-Fermi-level bookkeeping), Fermi level set in the gap at mid-gap 10.8335 eV, photon grid 0.01 to 6.00 eV, step 0.01 eV
  (omegamin 0.01 eV because the code prefactor 1/omega² is singular at 0).
- Phonon frequencies: interatomic constants from q2r.x with zasr='crystal' and EPW lifc=.true., asr_typ='crystal'.

## Mesh convergence (adopted Wannier set wv5)
| fine mesh | peak energy (eV) | peak mode | peak I (Å²/eV) | mode 9 max I (eV) | mode 12 max I (eV) | Frobenius peak F |
|---|---|---|---|---|---|---|
| 32³ | 2.45 | 12 (B1g, 340.8 cm⁻¹) | 47.57 | 41.18 (3.81) | 47.57 (2.45) | 33.6 (2.45, mode 12) |
| 48³ | 3.79 | 9 (A1g, 156.2 cm⁻¹) | 41.96 | 41.96 (3.79) | 36.21 (2.39) | 26.2 (3.79, mode 9) |
| 64³ | 3.80 | 9 (A1g, 156.2 cm⁻¹) | 40.11 | 40.11 (3.80) | 34.91 (2.37) | 25.3 (3.80, mode 9) |
| 80³ | — | queued, cancelled (never started) | — | — | — | — |
- 32³ is not converged: its global maximum is mode 12 at 2.45 eV, which moves to a lower value at 48³ and 64³.
- 48³ → 64³: peak energy unchanged within 0.01 eV, mode unchanged, magnitude −4.4%. Mode 12 changes −3.6%.
- Sensitivity to the Wannier set (48³): the superseded set (18 WF, frozen VBM-7..+6.5) gave 40.20 Å²/eV at 3.79 eV, mode 9.
  The adopted set differs by 4%. Both are in kernel/superseded/ and reported for transparency.

## Wannier-interpolation quality (DFT vs Wannier along G-A-B-G-C, 49 points; bandcheck/)
Deviations in meV, matched to the nearest DFT band at each k (bandcheck/wv5_compare.txt):
| Wannier band | DFT band | energy range (eV rel. VBM) | RMS | max |
|---|---|---|---|---|
| W01 | 19 | -10.9 .. -9.6 | 3.5 | 19.0 |
| W02 | 20 | -10.6 .. -7.8 | 2.3 | 8.0 |
| W03 | 21 | -5.8 .. -4.9 | 0.3 | 0.7 |
| W04 | 22 | -5.4 .. -4.2 | 0.4 | 1.3 |
| W05 | 23 | -4.6 .. -2.8 | 0.4 | 0.9 |
| W06 | 24 | -4.0 .. -2.5 | 0.3 | 0.9 |
| W07 | 25 | -4.0 .. -2.2 | 0.6 | 1.6 |
| W08 | 26 | -2.6 .. -1.8 | 0.5 | 2.0 |
| W09 | 27 | -1.9 .. -0.6 | 0.6 | 3.1 |
| W10 | 28 | -1.8 .. -0.4 | 0.6 | 3.1 |
| W11 | 29 (VBM) | -1.2 .. 0.0 | 0.9 | 3.6 |
| W12 | 30 (CBM) | 0.3 .. 2.6 | 1.2 | 4.9 |
| W13 | 31 | 1.8 .. 4.0 | 0.9 | 2.5 |
| W14 | 32 | 2.8 .. 4.4 | 1.3 | 6.0 |
| W15 | 33 | 2.9 .. 5.2 | 2.5 | 10.5 |
| W16 | 34 | 4.5 .. 5.9 | 33.2 | 231.7 |
| W17 | 35 | 4.6 .. 6.0 | 12.6 | 86.0 |
| W18 | 36 | 5.9 .. 8.2 | 986.8 | 2283.5 |
- Valence bands (W01–W11): RMS 1.3 meV, max 19 meV. Conduction bands W12–W15 (up to ~4.4 eV above the VBM): RMS ≤2.5 meV, max 10.5 meV.
- **Requirement not met above ~4.5 eV:** bands W16–W18 (conduction states at 4.5–8 eV above the VBM) fit poorly. The RMS over all
  conduction bands up to CBM+6 eV is 373 meV, dominated by W18. Kernel values for photon energies above ~4.5 eV carry this error.
  The adopted peak (3.8 eV) sits in the well-fitted region.
- Variants tried (bandcheck/*_compare.txt): 18 WF with frozen VBM-7..+6.5 (superseded); wv2 (froz VBM-6..+5): valence 1.3 meV, W16–18 bad;
  wv5 (froz VBM-6..+5.5, adopted): best valence and conduction to 4.4 eV; wv6 (froz to +6): deep band W02 49 meV rms;
  20-WF sets with outer window -2..+22 eV: fail (rms 200–700 meV). Choice: wv5.

## Gamma phonons (DFPT) and acoustic sum rule
- Raw ph.x (before ASR, cm⁻¹): acoustic -31.4 (A2u), 9.4 (Eu) x2; optical 45.3 (A2u), 61.7 (Eg) x2, 90.6 (Eu) x2, 156.2 (A1g),
  251.8 (Eu) x2, 340.8 (B1g), 367.2 (A2u), 412.9 (Eg) x2 (ph.x irrep labels, phrun/ph.out).
- The raw acoustic violation is large (about -35 cm⁻¹ for the simple-ASR pair). Not reduced further in this run; it is the main
  source of frequency uncertainty for the lowest optical modes.
- Crystal ASR (dynmat.x and q2r.x zasr='crystal', used for the kernel): acoustic 0, optical 51.1, 60.1 x2, 61.7 x2, 156.2,
  259.2 x2, 340.8, 372.0, 412.9 x2 cm⁻¹. Mode 9 (156.2 cm⁻¹) and mode 12 (340.8 cm⁻¹) are the same before and after ASR.
- Kernel mode list (EPW numbering, meV): 4: 6.33, 5-6: 7.46, 7-8: 7.65 (Eg, matches raw 61.7 cm-1), 9: 19.36 (A1g, exact), 10-11: 32.14, 12: 42.26 (B1g, exact), 13: 46.12, 14-15: 51.20 (Eg, matches raw 412.9 cm-1).
  Irrep labels for modes 4, 5-6, 10-11 and 13 are TENTATIVE: their frequencies shift under crystal ASR and I matched them by
  degeneracy and symmetry to the raw ph.x labels (A2u 45.3, Eu 90.6/251.8, A2u 367.2); eigenvector projection was not done.
- The simple-ASR route (EPW default, first run) gave two imaginary modes at -34.7 cm⁻¹, which EPW zeroed; that run is superseded.

## Compute
- node-hours: 8.83 (jobs.log: 47 Slurm jobs; processors/128 x elapsed; includes failed and superseded runs).
- wall-clock: about 12.5 h from the first calculation to DONE (limit 3 days); see RESULT.json wall_hours.

## Known limitations (stated, not fixed)
1. The code variant computes only the triangle diagram Gamma_c (indabs.f90, indabs_main); the source comment states that the
   Gamma_e / epvf17 diagram is out of scope in v1. The SI says diagrams c and e are both used. The kernel here is therefore the
   code's diagram (c) only, not the full paper kernel.
2. The paper does not define the "rotational invariant" explicitly; I used sum over 9 channels of |Gamma^ab| (per mode), and report
   the Frobenius norm as a cross-check (same mode and energy at the adopted mesh).
3. Wannier interpolation fails above ~4.5 eV (bands W16–W18), see the table. The 0–6 eV spectrum above 4.5 eV is less reliable.
4. Mesh convergence: 48³→64³ changes the magnitude by 4.4%; 80³ was not obtained (queued, cancelled).
5. Photon grid step 0.01 eV; the peak location is quoted to ±0.01 eV.
6. Phonon frequencies: crystal ASR; raw ASR violation ~35 cm⁻¹ (documented). LO-TO not included (centrosymmetric, epsil off).
7. Scalar-relativistic pseudopotentials (no SOC), as allowed by the task.
8. Process note: one shell command accidentally listed a directory outside the work root (names only, no content read); no other access outside the root.
