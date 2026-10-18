# REPORT — light-induced coherent-phonon generation kernel of wurtzite CdS (CdS_mp672, sealed cell)

Kernel Γ^{αβ}_s(ω_s; ω, −ω) of Hu, Guo, Li, Wang, Chang, evaluated with the authors' modified EPW
(toolchain qe-phnlo-75 on LUMI, `lindabs` branch), photon energies 0.01–6.00 eV, all nine Γ-point optical
modes of the 4-atom wurtzite cell. Adopted kernel file: `kernel/Gamma_alphabeta_s.dat` (fine mesh 96x96x51).

## 1. Result (identical to RESULT.json)

| quantity | value | source |
|---|---|---|
| largest rotational invariant I_s(ω) = Σ_{αβ} |Γ^{αβ}_s(ω)| in 0–6 eV | **486.58 Å²/eV** | `kernel/Gamma_alphabeta_s.dat`, block `imode = 4`, row ω = 5.79 eV (`analysis/kernel_invariant.py`) |
| photon energy of that peak | **5.79 eV** | same |
| dominating phonon mode | mode 4, **E2 (low)**, 4.7506 meV = **1.1487 THz** (38.3 cm⁻¹) | kernel-file block header; ph.x irrep table (`outputs/ph/ph.out`, "Mode symmetry, C_6v") |
| adopted fine k-mesh | **96x96x51** | `inputs/epw/epw_96x96x51.in` |
| compute | **9.10 node-hours** (of 20) | `jobs.log` |
| wall time | 9.5 h (START_TIME → DONE) | `START_TIME`, `DONE` |

Mode 4 is one partner of the doubly degenerate E2(low) pair (modes 4 and 5, both 4.7506 meV). The split of the
pair's weight between the two partners depends on the (arbitrary) basis chosen in the degenerate subspace by the
diagonaliser; the pair sum I_4 + I_5 is basis independent (951.1 Å²/eV at 5.79 eV on 96x96x51). RESULT.json follows
the task definition (per-mode magnitude) and reports the larger partner, mode 4.

The soft-mode frequency in the kernel file (4.7506 meV = 38.32 cm⁻¹, EPW with asr_typ = 'crystal') differs by
0.08 cm⁻¹ from dynmat.x with asr = 'crystal' (38.40 cm⁻¹); the two codes apply the sum rule with slightly
different numerics. All other modes agree to 0.01 meV. RESULT.json uses the kernel-file value.

Per-mode peaks on the adopted mesh (I_s in Å²/eV, 0 < ω ≤ 6 eV):

| mode | irrep | ħω_s (meV) | f (THz) | ω_peak (eV) | I_peak |
|---|---|---|---|---|---|
| 4 | E2 | 4.7506 | 1.1487 | 5.79 | 486.6 |
| 5 | E2 | 4.7506 | 1.1487 | 5.79 | 464.5 |
| 6 | B1 | 16.7097 | 4.0404 | 4.37 | 162.1 |
| 7 | A1 | 29.0666 | 7.0283 | 4.39 | 250.1 |
| 8 | E1 | 29.9787 | 7.2488 | 4.38 | 80.5 |
| 9 | E1 | 29.9787 | 7.2488 | 5.54 | 22.8 |
| 10 | E2 | 31.6797 | 7.6601 | 5.79 | 157.0 |
| 11 | E2 | 31.6797 | 7.6601 | 5.79 | 89.2 |
| 12 | B1 | 37.4833 | 9.0634 | 4.31 | 143.6 |

(B1 modes are silent in C6v and formally should not couple to a two-photon Raman-type process at q = 0; the code
evaluates every optical mode and the B1 values are reported as written. The A1 channel obeys xx = yy, xy = 0,
as required by symmetry; the E modes mix xx/yy/xy within the degenerate pair.)

## 2. Mesh convergence of the kernel

Fine k-meshes with Nz ≈ N·|b3|/|b1| = N/1.88 (hexagonal cell, c/a = 1.627). Same Wannier data, same settings
(η = degaussw = 25 meV, 600 photon energies, 26 bands, no symmetry reduction). All files kept in `kernel/`.

| mesh | k-points | global peak: mode / ω (eV) / I (Å²/eV) | E2(low) pair sum at peak | A1 (mode 7) peak | node-h |
|---|---|---|---|---|---|
| 24x24x13 | 7 488 | 4 / 5.81 / 500.4 | 983.9 (5.81 eV) | 325.5 @ 4.46 eV | 0.08 (64 ranks) |
| 48x48x26 | 59 904 | 4 / 5.80 / 477.0 | 930.0 (5.80 eV) | 261.2 @ 4.45 eV | 0.88 |
| 72x72x38 | 197 136 | 4 / 5.79 / 489.2 | 955.2 (5.79 eV) | 251.1 @ 4.46 eV | 2.92 |
| **96x96x51** | 470 016 | **4 / 5.79 / 486.6** | 951.1 (5.79 eV) | 250.1 @ 4.39 eV | 5.05 |

72x72x38 → 96x96x51: peak value −0.5 %, peak position unchanged (0.01 eV grid), A1 peak −0.4 %. The peak is
converged to better than 1 % with the 25 meV broadening; the next mesh in the sequence (120x120x64, ≈ 13 node-h)
does not fit in the remaining budget (10.9 node-h) and was not run. The spectrum is a dense set of
double-resonance features; only its envelope near the window edge (e.g. I_4(6.00 eV): 29, 228, 152, 182 Å²/eV
for the four meshes) is still mesh-sensitive, the peak itself is not.

## 3. Wannier interpolation quality (DFT vs Wannier bands)

pw.x `bands` on exactly the 181 k-points of the Wannier90 band path Γ–M–K–Γ–A–L–H–A
(`outputs/epw/bands_w90.out`, `inputs/epw/bands_w90.in`) compared band by band with `outputs/epw/cds_band.dat`
(26 Wannier bands; data `analysis/wannier_vs_dft_bands.dat`, statistics `analysis/wannier_vs_dft_stats.txt`,
script `analysis/compare_bands.py`). The 8 Cd 4s/4p semicore bands (−94, −56 eV) are excluded from the Wannier
subspace. VBM = 7.068 eV, CBM = 8.309 eV (PBE gap 1.24 eV, direct at Γ).

| band set | RMS deviation | max deviation | points |
|---|---|---|---|
| all 18 valence bands (S 3s, Cd 4d, S 3p) | 0.35 meV | 2.9 meV | 3258 |
| conduction bands up to CBM + 4.0 eV | 1.0 meV | 3.6 meV | 396 |
| conduction bands up to CBM + 5.3 eV (top of frozen window, 13.6 eV) | 2.3 meV | 13.3 meV | 720 |
| conduction bands up to CBM + 6.0 eV | 68 meV | 357 meV | 1019 |

With 26 WFs (Cd s,p,d + S s,p) only 8 conduction bands are spanned; the frozen window ends at 13.6 eV
(= VBM + 6.5 eV) and Wannier bands 22–26 deviate from DFT above it (up to 0.8 eV at 15–17 eV). Every
electronic resonance ε_c − ε_v = ħω ≤ 6 eV terminates below VBM + 6 eV = 13.07 eV, i.e. inside the frozen window,
where the interpolation is within a few meV; the bands above 13.6 eV enter only as off-resonant intermediate
states in the phonon-resonant denominator 1/(ħω_s + ε_ln + iη). Within the budget this was accepted rather than
re-Wannierising with a larger set (which would have required redoing all meshes).

Wannier90 run inside EPW (`outputs/epw/cds.wout`): disentanglement converged (Ω_I = 36.88 Å²), 1000 Wannierisation
iterations (num_iter limit), total spread 43.68 Å² (Cd sp 3.1–3.3, Cd d 0.66–0.85, S sp 1.35–1.38 Å²);
`inputs/w90/cds.win`.

## 4. Γ-point phonons (DFPT, ph.x, q = Γ, tr2_ph = 1e-16, epsil = .true.) with the acoustic sum rule

Raw ph.x (`outputs/ph/ph.out`): acoustic 1.8, 2.5, 2.5 cm⁻¹ before the sum rule. After dynmat.x with
asr = 'crystal' (`outputs/ph/dynmat.out`, `inputs/ph/dynmat.in`):

| modes | irrep (C6v, ph.x) | activity | ω (cm⁻¹) | ω (THz) | ħω (meV) |
|---|---|---|---|---|---|
| 1–3 | A1 + E1 (acoustic) | | 0.00 | 0.0000 | 0.000 |
| 4–5 | E2 (low) | R | 38.40 | 1.1512 | 4.761 |
| 6 | B1 | silent | 134.77 | 4.0404 | 16.710 |
| 7 | A1 (TO) | IR + R | 234.45 | 7.0286 | 29.069 |
| 8–9 | E1 (TO) | IR + R | 241.81 | 7.2494 | 29.982 |
| 10–11 | E2 (high) | R | 255.52 | 7.6603 | 31.680 |
| 12 | B1 | silent | 302.35 | 9.0643 | 37.486 |

No q-direction was given, so no LO–TO splitting (the kernel is evaluated at q = 0 exactly, lpolar = .false.).
ε∞ = diag(6.105, 6.105, 6.159); Born charges Z*(Cd) = diag(2.108, 2.108, 2.196) e (before the charge-neutrality
correction, ‖ΔZ*‖ = 8.9e-3). EPW (asr_typ = 'crystal') reproduces these within 0.01 meV except the soft E2 mode
(4.7506 vs 4.761 meV, see §1). Acoustic modes are excluded from the kernel by eps_acoustic = 5 cm⁻¹.

## 5. Cell, structure and computational settings

* Cell used (Å, rows = lattice vectors, verbatim from `structure.cif`/`structure_POSCAR`, no vc-relax):
  a1 = (2.06064203, −3.56913669, 0), a2 = (2.06064203, 3.56913669, 0), a3 = (0, 0, 6.70487960);
  a = 4.1213 Å, c = 6.7049 Å. Species Cd, Cd, S, S at (2/3, 1/3, 0.50022255), (1/3, 2/3, 0.00022255),
  (2/3, 1/3, 0.87677745), (1/3, 2/3, 0.37677745) (the file's 0.333333/0.666667 written as 1/3, 2/3 to 10 digits).
  A fixed-cell BFGS relaxation (`inputs/scf/relax.in`, `outputs/scf/relax.out`) found forces of 7e-5 Ry/bohr on
  these positions (< forc_conv_thr 1e-4), so they were kept unchanged. Residual stress in the sealed cell: +30 kbar.
* DFT: QE 7.5, PBE, PseudoDojo nc-fr-04 standard NC pseudopotentials (Cd 20 e, S 6 e; `inputs/Cd.upf`, `inputs/S.upf`)
  used scalar-relativistically (no SOC); ecutwfc = 100 Ry; 9x9x6 Γ-centred k-mesh; 12 symmetry operations.
* DFPT: q = Γ only (nq = 1x1x1); Γ is on the coarse q-grid, so the Γ phonons and e–ph matrix elements enter EPW
  without q-interpolation.
* Wannier/EPW: NSCF on the full 9x9x6 grid (486 k, 40 bands, explicit list in [0,1)), 26 WFs, windows
  [−6, 20] / frozen [−6, 13.6] eV, vme = 'wannier'. Kernel: lindabs = .true., omega 0.01…6.00 eV step 0.01
  (ω = 0 excluded: 1/ω² prefactor), degaussw = 0.025 eV (η = 25 meV as in the paper), fsthick = 100 eV (all 26 bands),
  efermi_read with fermi_energy = 7.69 eV (mid-gap), temps = 300, eps_acoustic = 5 cm⁻¹, lpolar = .false.,
  mp_mesh_k = .false. The v1 code implements the triangle diagram (g, h, h with the phonon-resonant denominator);
  the g^{s;α} vertex term is marked out of scope in the code.
* Invariant: I_s(ω) = Σ over the nine written Cartesian channels (xx, yy, zz, xy, xz, yz, yx, zx, zy) of
  |Γ^{αβ}_s(ω)| in Å²/eV, per mode; the maximum over modes and 0 < ω ≤ 6 eV gives peak_ev / peak_a2_per_ev.

## 6. Compute (`jobs.log`)

| job | purpose | partition | nodes × h | node-h |
|---|---|---|---|---|
| 22921749 | pw.x relax test | debug | 0.25 × 0.02 | 0.005 |
| 22921770 | scf + ph.x (input error) | debug | 0.5 × 0.004 | 0.002 |
| 22921771 | placeholder (exited, 2 s) | small | 1 × 0.0006 | 0.001 |
| 22921780 | ph.x Γ + dynmat + pp.py | debug | 0.5 × 0.094 | 0.047 |
| 22921847 | bands + nscf + EPW Wannier + kernel 24x24x13 | debug | 0.5 × 0.37 | 0.185 |
| 22922082 | bands on W90 path + kernels 24/48/72 | small | 1 × 3.81 | 3.81 |
| 22923502 | kernel 96x96x51 | small | 1 × 5.046 | 5.046 |
| **total** | | | | **9.10** |

Partition choice: standard had 578 pending jobs and a predicted 2-day start when the long jobs were submitted;
small started within 3 h, debug was used only for runs under 10 min. Remote wavefunctions and ph.x scratch
files were deleted after use; the Wannier/EPW data (`calc/epw`, 0.66 GB) and `calc/ph/save` were kept.

## 7. Files

* `kernel/Gamma_alphabeta_s.dat` (adopted, = `_96x96x51`), `kernel/Gamma_alphabeta_s_{24x24x13,48x48x26,72x72x38}.dat`
* inputs: `inputs/scf` (relax, scf), `inputs/ph` (scf, ph, dynmat), `inputs/epw` (nscf, bands, bands_w90, epw1,
  epw_96x96x51, mesh template, k lists), `inputs/w90/cds.win`, `inputs/jobs/*.sh` (Slurm scripts)
* outputs: `outputs/scf`, `outputs/ph` (ph.out, dynmat.out, cds.dyn1), `outputs/epw` (epw1.out, cds.wout,
  cds_band.dat, bands.out, bands_w90.out, mesh runs), `outputs/epw96` (epw_96x96x51.out, Pi_0)
* analysis: `analysis/kernel_invariant.py`, `analysis/compare_bands.py`, `analysis/make_result.py`,
  `analysis/wannier_vs_dft_bands.dat`, `analysis/wannier_vs_dft_stats.txt`
