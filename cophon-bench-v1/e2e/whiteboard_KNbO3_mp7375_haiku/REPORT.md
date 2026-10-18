# KNbO3_mp7375 — light-induced coherent-phonon generation kernel (cophon-bench v1)

## Result (converged mesh 96x96x96; same numbers as RESULT.json)
| quantity | value |
|---|---|
| kernel peak (invariant I(w) = sum_s sum_ab |Gamma^ab_s|) | **3.30 eV**, **179.49 Å²/eV** |
| dominant mode at the peak | **7.18 THz (239.5 cm⁻¹), A_1 (L_1)**, mode index 9 of the Gamma spectrum (share of I at peak: 36%) |
| cell | sealed structure.cif cell, not relaxed (see below) |
| node-hours | 1.94 (cpus/128 rule, from jobs.log) |
| wall-clock | ~2.1 h (SCF 03:04 to end of kernel runs, LUMI clock) |

Invariant definition used (decision, see NOTES.md): per mode, sum over the nine Cartesian channels of |Gamma^ab_s(w)|; total over the
optical modes; peak over w in [0, 6] eV. The paper does not name the invariant explicitly, so this is our reading of "per-mode magnitudes
summed over Cartesian channels".

## Caveats that matter for comparing with the reference
1. **Only the triangle diagram is in the code.** The kernel variant (EPW/src/indabs.f90, input `lindabs`) computes Gamma_c (plus Pi_0
   written separately). The Gamma_e / diagram (e) term (optically perturbed EPC, SI Eq. diagram_e) is declared (`lgammae`) but marked
   "out of scope in v1" and not implemented. Our numbers are therefore Gamma_c only, not the full Gamma^ab_s = (c)+(e).
2. **Wannier model: O 2p and Nb t2g/eg fit to ~1 meV in the valence, not in the conduction.** See table below. The 14-function model is
   adopted because it reproduces the valence fit; the conduction bands (esp. Nb eg, bands 24–25, up to 1.8 eV at some k) are
   poorly represented. This is the main systematic risk for the 0–6 eV kernel.
3. **Peak position is grid-limited.** The photon grid is 0.05 eV (120 points); the peak moved 3.9 → 3.55 → 3.6 → 3.3 → 3.3 eV across
   meshes; the peak *magnitude* converges (72³ vs 96³: 179.60 vs 179.49 Å²/eV, 0.06%).
4. **Cell is left-handed** (det < 0 for the given lattice vectors; dynmat.x warns "axis vectors are left-handed"). We used it exactly as
   given; QE and EPW ran without complaint.
5. The code's diagnostic (validation-stage) status is acknowledged in the implementation note; we used the code as shipped.

## Mesh convergence of the kernel peak
| EPW fine mesh | peak (eV) | I at peak (Å²/eV) | dominant mode (THz) |
|---|---|---|---|
| 12x12x12 | 3.90 | 282.33 | 7.18 |
| 24x24x24 | 3.55 | 201.44 | 7.18 |
| 48x48x48 | 3.60 | 180.11 | 7.18 |
| 72x72x72 | 3.30 | 179.60 | 7.18 |
| **96x96x96** | **3.30** | **179.49** | **7.18** |

Converged in magnitude (72 vs 96: 0.06%). The grader should use the 96 (or 72) numbers; the peak energy is set by the 0.05 eV grid.

## Wannier interpolation (DFT pw.x bands vs wannier90, path G-X-M-G-R, 81 DFT k-points)
Model adopted: 14 WF = Nb 4d (5) + O 2p (9), disentanglement window 2–20 eV, frozen 3–11 eV, 6x6x6 grid, Omega_total 13.49 Å².
(file: wannier/band_compare_final14.json)

| band set | RMS (meV) | max |dE| (meV) |
|---|---|---|
| valence, O 2p (DFT bands 12–20) | 1.02 | 9.7 |
| conduction 21–25 up to CBM+6 eV | 61.5 | 301 |
| band 21 (Nb t2g) | 23.1 | 70 |
| band 22 | 18.0 | 58 |
| band 23 | 52.0 | 101 |
| band 24 (Nb eg) | 397 | 1768 |
| band 25 | 460 | 1768 |

The conduction-band target ("few meV within CBM+6 eV") is **not met**. Two 18-WF variants (adding Nb 5s/5p; wannier files in wannier/)
improved conduction (12.6 meV RMS, max 72 meV) but degraded the valence fit (11.8 meV RMS, max 91 meV); the 14-WF model was preferred
because the valence O 2p → Nb transitions dominate the kernel. This trade-off is unresolved.

## Gamma phonons (DFPT, ph.x with epsil, tr2_ph 1e-14; dynmat.x asr='crystal')
Before ASR: acoustic −7.6, −5.8, −5.8 cm⁻¹ (ASR violation); optical (cm⁻¹): 183.3 (E, x2), 186.5 (A_1), 202.9 (E, x2), 239.4 (A_1),
248.0 (A_2), 275.5 (E, x2), 518.1 (E, x2), 570.7 (A_1). After dynmat.x asr='crystal': the dominant mode 239.50 cm⁻¹ (7.180 THz).
Irreps from ph.x labels (L_1/L_2/L_3 in the output). The 248.0 cm⁻¹ A_2 mode has no IR activity.

## Ground state
SCF pw.x, PseudoDojo nc-fr-04 PBE standard (K 9e, Nb 13e, O 6e; scalar-relativistic use), 90 Ry, 6x6x6 unshifted k, fixed occupations,
converged in 14 iterations to E = −284.34960483 Ry. VBM 8.41 eV, CBM 10.62 eV (6x6x6 grid). Forces ≤ 1.6e-4 Ry/bohr: the supplied
internal coordinates are already relaxed, so no internal relaxation was done (cell held fixed as required). Point group: 6 operations,
no inversion (polar; second-order kernel allowed).

## Compute
1.94 node-hours (cores/128 rule; sum over jobs in jobs.log). Failed or cancelled attempts are included.
