# REPORT — light-induced coherent-phonon generation kernel of Bi2O2Se (cophon-bench v1, whiteboard arm)

Status: DRAFT — kernel numbers are filled in at the end (see RESULT.json for the declared values).

## 1. Crystal and cell (sealed)
Body-centred tetragonal Bi2O2Se, space group I4/mmm (D4h), 5-atom primitive cell used exactly as given in
`structure.cif` / `structure_POSCAR`:

| | x (Å) | y (Å) | z (Å) |
|---|---|---|---|
| a1 | -1.96469684 | 1.96469684 | 6.20630152 |
| a2 | 1.96469684 | -1.96469684 | 6.20630152 |
| a3 | 1.96469684 | 1.96469684 | -6.20630152 |

(conventional a = 3.92939 Å, c = 12.41260 Å; V = 95.81 Å³). Positions (crystal): Bi (0.35312528, 0.35312528, 0),
Bi (0.64687472, 0.64687472, 0), Se (0, 0, 0), O (0.25, 0.75, 0.5), O (0.75, 0.25, 0.5). No cell relaxation. An
internal-coordinate relaxation (pw.x `relax`, BFGS) at the fixed cell took 0 steps: the sealed positions are already the
equilibrium of this setup (max force 5e-5 Ry/bohr, residual pressure 0.24 kbar). The given positions were therefore used.

## 2. DFT setup
- QE 7.5 (toolchain `qe-phnlo-75`), PBE, PseudoDojo nc-fr-04 standard pseudopotentials (Bi-d, O, Se-d; 58 valence
  electrons) used scalar-relativistically (no SOC), ecutwfc = 90 Ry, fixed occupations, 12x12x12 Γ-centred k-mesh for
  SCF/DFPT (163 irreducible points, conv_thr 1e-12 for the production SCF).
- PBE band structure (pw.x `bands`, 201 points on the BCT2 path Γ-X-Y-Σ-Γ-Z-Σ1-N-P-Y1-Z): VBM = 10.674 eV on Σ-Γ,
  CBM = 10.998 eV at Γ, indirect gap 0.324 eV, smallest direct gap 1.25 eV. Mid-gap Fermi level 10.836 eV used in EPW.

## 3. Γ phonons (DFPT, ph.x, tr2_ph = 1e-16, epsil = .true.; dynmat.x with asr = 'crystal')
||dyn(ASR) − dyn|| = 5.3e-4; raw acoustic frequencies −3.4/−3.1 cm⁻¹ → 0 after ASR. ε∞ = 14.58 (xx), 10.72 (zz);
Z*(Bi) = 6.23/5.47, Z*(Se) = −4.43/−3.18, Z*(O) ≈ −3.97 (mean).

| modes | ω (cm⁻¹) | ω (THz) | ω (meV) | irrep (ph.x, D4h) | activity |
|---|---|---|---|---|---|
| 1–3 | 0.00 | 0.000 | 0.000 | A2u + Eu | acoustic |
| 4–5 | 14.67 | 0.4399 | 1.819 | Eu | IR |
| 6 | 43.15 | 1.2936 | 5.350 | A2u | IR |
| 7–8 | 61.65 | 1.8482 | 7.644 | Eg | Raman |
| 9 | 155.59 | 4.6646 | 19.291 | A1g | Raman |
| 10–11 | 251.36 | 7.5356 | 31.164 | Eu | IR |
| 12 | 339.57 | 10.1800 | 42.102 | B1g | Raman |
| 13 | 364.09 | 10.9152 | 45.142 | A2u | IR |
| 14–15 | 414.97 | 12.4406 | 51.449 | Eg | Raman |

EPW reads the same dynamical matrix and reports (meV): 0, 0, 0, 1.901 (x2), 5.413, 7.662 (x2), 19.291, 31.164 (x2),
42.094, 45.148, 51.433 (x2) — identical within 0.1 cm⁻¹; the EPW mode energies in the kernel file are these values.
(The A1g Raman line at 155.6 cm⁻¹ agrees with the experimental ~159 cm⁻¹.)

## 4. Wannier interpolation (EPW-internal wannier90; 8x8x8 coarse k-grid, nscf nbnd = 80)
20 Wannier functions from Bi s,p / O s,p / Se s,p projections for DFT bands 16–35 (O 2s, Bi 6s, Se 4s, O 2p, Se 4p,
Bi 6p); bands 1–15 (Se 3d, Bi 5d, below −22 eV) excluded. Disentanglement window [−9.5, 20.7] eV (absolute), frozen
window [−9.5, 15.7] eV = up to VBM + 5.0 eV (DFT band 36 enters at VBM + 5.7 eV, so the Bi-6p manifold is not isolated
above that). 2000 minimisation steps; total spread 27.69 Å² (Ω_I = 23.22 Å²).
Comparison of the EPW-interpolated bands (band_plot, `wannier/wannier_bands_bct2_path.eig`) with DFT
(`wannier/dft_bands_bct2_path.dat`) at the same 201 k-points (`wannier/comparison_summary.txt`):

| window (relative to VBM) | points | RMS (meV) | max (meV) |
|---|---|---|---|
| all 14 valence bands (−20.2 … 0) | 2814 | 0.32 | 1.13 |
| conduction 0.23 … +5.03 eV (frozen window) | 963 | 3.1 | 73 (band 34 at the window top, Z) |
| conduction 0.23 … +6.03 eV | 1206 | 24 | 232 (bands 34–35 above the frozen window) |

Per band: valence ≤ 1.1 meV, CBM band 2.8 meV, next three conduction bands 2.4 / 4.8 / 9.9 meV. The two highest
Wannier bands are exact only below VBM + 5 eV; between 5 and 6 eV above the VBM they deviate (up to 0.2 eV), which is the
main approximation of the model for photon energies in the 5–6 eV range.

## 5. Kernel calculation (modified EPW, "kernel variant")
`lindabs = .true.` drives `indabs_main`, which in this build accumulates the triangle diagram Γ|_c of the paper
(Gamma_alphabeta_s, Å²/eV; the Γ|_e vertex term is not implemented in this port — `lgammae` has no consumer) at q = Γ,
on the full fine k-mesh (no symmetry reduction), with Gaussian deltas of width degaussw = 0.025 eV (the paper's η),
photon energies 0.01 … 6.00 eV in 0.01 eV steps, fsthick = 8 eV around the mid-gap Fermi level (16 Wannier bands,
2.85–16.7 eV absolute, enter), eps_acoustic = 10 cm⁻¹ (only the three acoustic modes skipped), vme = 'wannier',
lpolar = .false., coarse q-grid 1x1x1 (Γ only; the kernel needs only q = 0).
Rotational invariant used for RESULT.json: I_s(ω) = Σ_{αβ} |Γ^{αβ}_s(ω)| over the nine Cartesian channels, per mode;
the Frobenius norm is listed as well.

### Mesh convergence
Full Γ-centred fine meshes N×N×N (N = 12, 24, 32, 36, 48, 64; 96 and 128 pending at the time of this draft). Peak of
I_s(ω) per even mode (Å²/eV; photon energy of the peak in eV in parentheses); files `kernel/Gamma_alphabeta_s_<mesh>.dat`,
table in `kernel/convergence_table.txt`:

| mode (irrep, meV) | 12³ | 24³ | 32³ | 36³ | 48³ | 64³ |
|---|---|---|---|---|---|---|
| A1g (19.29) | 56.4 (1.80) | 40.9 (3.80) | 41.6 (3.81) | 39.9 (3.81) | 42.0 (3.79) | 40.4 (3.80) |
| B1g (42.09) | 74.1 (2.33) | 46.3 (2.55) | 46.1 (2.46) | 38.4 (2.44) | 35.9 (2.39) | 34.9 (2.37) |
| Eg (7.66) | 26.3 (2.95) | 15.5 (2.94) | 15.3 (2.90) | 15.1 (2.90) | 15.4 (2.91) | 15.7 (2.90) |
| Eg (51.43) | 15.7 (4.19) | 11.1 (4.18) | 11.4 (4.16) | 12.8 (4.16) | 12.3 (4.16) | 12.2 (4.15) |
| odd modes, max | 1.98 | 0.81 | 0.74 | 0.69 | 0.64 | 0.63 |

The 12³–32³ maxima are dominated by mesh spikes (the fixed 25 meV Gaussian is narrower than the band-energy change per
mesh step); from 36³ on the global maximum is the A1g mode at 3.79–3.81 eV with a height fluctuating by ±3 %
(39.9 / 42.0 / 40.4 Å²/eV), while the B1g maximum settles near 35 Å²/eV at 2.37–2.39 eV. The peak *position* is converged to
±0.01 eV from 24³ on.

### Symmetry check
Only even (Raman-active: A1g, B1g, 2 Eg) modes can carry the kernel in a centrosymmetric crystal; the odd (Eu, A2u) modes
come out 1–3 % of the leading values (slight symmetry breaking of the off-centred Wannier gauge), see Section 6.

## 6. Results
(to be filled)

## 7. Compute
(to be filled from jobs.log)
