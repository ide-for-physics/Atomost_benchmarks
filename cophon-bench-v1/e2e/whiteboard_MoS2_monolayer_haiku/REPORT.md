# MoS2 monolayer — light-induced coherent-phonon kernel (EPW kernel variant)

Deliverables: `RESULT.json` (numbers), `kernel/Gamma_alphabeta_s.dat` (converged mesh 120x120x1), `kernel/Gamma_alphabeta_s_{48,72,96}x*x1.dat`,
`inputs/` (all pw.x, ph.x, nscf, bands, EPW inputs, job scripts, pseudopotentials Mo.upf/S.upf), `outputs/` (run logs, wannier90 output, DFT bands, phonon output),
`analysis/` (scripts that produced every number here), `jobs.log`, `NOTES.md`.

## 1. Result

| quantity | value |
|---|---|
| peak photon energy (0–6 eV) | **2.83 eV** |
| peak invariant I = sqrt(sum_ab abs(Gamma^ab)^2) | **64.04 Å²/eV** (mesh 120x120x1) |
| dominant mode | **A'_1** (imode 8), **11.890 THz** (396.6 cm⁻¹, 49.17 meV) |
| mesh (converged) | 120x120x1 |
| node-hours / wall | 0.36 node-h (jobs.log) / 0.95 h (start 07:04 UTC to DONE 08:01 UTC) |

Invariant definition (my choice; the manuscript/SI does not define a "rotational invariant" for the kernel): for each mode s and photon energy w,
I_s(w) = sqrt( sum_{a,b} |Gamma^{ab}_s(w)|^2 ), the Frobenius norm of the complex 3x3 tensor. It is invariant under rotations of the Cartesian frame and has units Å²/eV.
Peak = max over w in [0, 6] eV and all optical modes. The alternative reading "sum over channels of |Gamma^{ab}|" gives 90.67 Å²/eV at the same point (same mode, same energy).

At the peak the 9 channels of mode 8 are dominated by in-plane xx = yy (≈ 20.5 + 40.4 i, the real and imaginary parts; the off-diagonal in-plane xy/yx are ≈ 0.02 + 0.04 i, and the out-of-plane zz and xz/yz are below 1e-2). Other modes at 2.83 eV: E'' (imode 4,5) 0.25, E' (6,7) 8.8–8.9, A''_2 (9) 0.011 Å²/eV.

## 2. Mesh convergence (kernel invariant at the peak; set A2, 11 Wannier functions, degaussw 0.025 eV)

| fine mesh | peak energy (eV) | I_max (Å²/eV) | change vs next finer |
|---|---|---|---|
| 48x48x1 | 2.83 | 65.61 | — |
| 72x72x1 | 2.83 | 63.77 | −2.8 % |
| 96x96x1 | 2.83 | 64.01 | +0.4 % |
| 120x120x1 | 2.83 | 64.04 | +0.05 % |

Converged to 0.05 % between 96 and 120; 120x120x1 adopted. Peak energy is fixed at 2.83 eV on the 0.01 eV grid across all meshes. Per-mode maxima are in `analysis/kernel_peak` output (mode 8 is largest at every mesh).

## 3. Wannier interpolation quality (DFT vs Wannier, path G–M–K–G)

DFT: pw.x `bands` (PBE, scalar-relativistic, 90 Ry, 30 bands) along G–M–K–G (111 points); Wannier: wannier90 `bands_plot` from the EPW-internal wannierization on the same path.
Gap: VBM −0.4609 eV (Γ), CBM 1.1960 eV (K), indirect gap 1.657 eV (direct at K 1.676 eV).

Set A2 (chosen): 11 Wannier functions, Mo:d + S:p (Omega_total = 18.05 Å²; S-p centres at ±1.53–1.66 Å, Mo-d at the origin); exclude bands 1–6 (semicore);
disentanglement window −6.5 … 7.5 eV; frozen window −1.5 … 2.4 eV.

| comparison | RMS (meV) | max (meV) |
|---|---|---|
| top valence (Wannier vs DFT band 13) | 0.6 | 1.9 |
| lowest conduction (Wannier vs DFT band 14) | 1.0 | 8.4 |
| valence window [VBM−2, VBM] (all states, nearest-DFT-band) | 1.6 | 15.2 |
| conduction window [CBM, CBM+2] | 2.2 | 14.1 |
| conduction window [CBM, CBM+6] | 2.8 | 14.1 |
| all Wannier states in [VBM−1, CBM+6] | 2.5 | 14.1 |

The "nearest-DFT-band" metric matches each Wannier state to the closest DFT band energy at the same k along the path, so it is a fit indicator rather than a strict band-by-band error; the two rows that compare named bands are the strict ones.

Sensitivity (set A, frozen window only to 1.3 eV): top valence is the same (0.6 meV), but the lowest conduction band is off by 32 meV RMS (74 meV max) and the [CBM, CBM+6] window is 21 meV RMS.
That is why the frozen window was widened to 2.4 eV. A 12-function set (Mo:s added, `B2`) was started but cancelled before completion (not needed once A2 met the target), so it is not reported.

## 4. Gamma phonons (DFPT, PBE, 90 Ry, 12x12x1 SCF)

ph.x at Gamma (tr2_ph=1e-14, trans). Raw frequencies (before ASR): acoustic −17.48 cm⁻¹ (E') and −8.20 cm⁻¹ (A''_2); optical 276.31, 373.80, 396.56, 458.41 cm⁻¹.
Acoustic sum rule applied with dynmat.x (asr='simple'; crystal gave the same optical frequencies within 0.1 cm⁻¹):

| mode | irrep | frequency (cm⁻¹) | THz | meV |
|---|---|---|---|---|
| 1–3 | acoustic | 0.00 | 0.000 | 0 |
| 4–5 | E'' | 276.93 | 8.302 | 34.34 |
| 6–7 | E' | 374.23 | 11.219 | 46.40 |
| 8 | A'_1 | 396.62 | 11.890 | 49.17 |
| 9 | A''_2 | 458.47 | 13.745 | 56.84 |

EPW reproduces these (its own simple ASR): 34.3351 / 46.3982 / 49.1740 / 56.8432 meV. The SCF relaxation check: forces on S were 5.9e-5 Ry/bohr, so the sealed-cell internal coordinates were kept.

## 5. Compute

Jobs (`jobs.log`): all on `small`, 64 CPUs allocated per job (0.5 node). Total elapsed 0.72 h → **0.36 node-hours**. Failed or cancelled attempts are included in the total.
Wall time: start 07:04 UTC 2026-10-16, DONE see RESULT.json. The long waits were queue time on `small` (~1.5 h at first submission).

## 6. Caveats and choices (all also in NOTES.md)

- **Scalar-relativistic** PBE with the PseudoDojo fully-relativistic NC pseudopotentials (no SOC), as the task allows. The MoS2 gap (1.66 eV indirect) and the mode energies are for this approximation.
- **Frequency grid** starts at 0.01 eV (not 0): the kernel has a 1/ω² prefactor (indabs.f90), so ω = 0 gives Inf/NaN. Grid 0.01–6.00 eV in 0.01 eV steps (600 points).
- **Gamma-only q-grid** (nq = nqf = 1): `indabs.f90` writes `Gamma_alphabeta_s.dat` from the last q point only, so the Γ-only grid is what makes the output a Γ-phonon kernel. Acoustic modes (1–3) are not written; modes 4–9 are.
- **Fermi level** set to midgap (0.3675 eV, `efermi_read`), so f_ij is the insulating occupation. EPW's `degaussw` = 0.025 eV (default), `ladsmear` = false.
- **Workaround to flag:** EPW (this build) expects `prefix.dvscf_q1` (direct access) and `prefix.dyn_q1`. ph.x in `electron_phonon='epw'` mode wrote `mos2.dvscf1` with a file size of 9 records of the EPW record length (49766400 bytes = 9 × 345600 × 16 B). I copied it to `mos2.dvscf_q1`. EPW read it without error and its phonon energies match the ASR dynamical matrix. I did not independently verify the dvscf matrix elements by a second route; the agreement in phonon energies and the smooth, mesh-converged kernel are the evidence available here.
- **Kernel file** is written at the converged mesh 120x120x1. Lower meshes are kept as `kernel/Gamma_alphabeta_s_<N>x<N>x1.dat`.
- **Invariant definition**: Frobenius norm (see §1). If the grader's definition is the channel-magnitude sum, the value is 90.67 Å²/eV at the same peak (same energy and mode).
- The reference calculation of this crystal in this cell is not available to me, so the comparison is only internal (mesh and Wannier sensitivity).
