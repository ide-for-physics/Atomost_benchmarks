# SnS2 (mp-1170, sealed cell) — light-induced coherent-phonon generation kernel Γ^{αβ}_s(ω_s; ω, −ω)

Code: Quantum ESPRESSO 7.5 + the authors' kernel-variant EPW (`qe-phnlo-75` toolchain on LUMI), `lindabs = .true.`, output file
`Gamma_alphabeta_s.dat`. All numbers below come from files in `run/` (inputs + outputs) and `kernel/` (kernel files); jobs in `jobs.log`.

## Result (RESULT.json)

| quantity | value | source |
|---|---|---|
| adopted fine k-mesh | 192x192x96 (q = Γ only) | `run/17_kernel18_k192/epw2.in` |
| peak of the invariant S_s(ω) = Σ_{αβ} \|Γ^{αβ}_s\| in 0–6 eV | **5.46 eV** | `kernel/Gamma_alphabeta_s.dat`, `scripts/analyze_kernel.py` |
| peak value | **77.19 Å²/eV** (7.718976e+01) | same |
| dominating mode | **A1g, 38.6486 meV = 9.3452 THz** (mode 8 of 9; DFPT+ASR dynmat: 311.73 cm⁻¹ = 9.3455 THz) | `run/03_ph/out/dynmat.log`, `run/03_ph/out/ph.out` (mode symmetry, D3d) |
| compute | 4.841 node-hours | `jobs.log` |

Invariant: per mode s and photon energy ω, the sum over the nine Cartesian channels of |Γ^{αβ}_s(ω_s; ω, −ω)|, i.e. the per-mode magnitudes
summed over channels (SI Eq. for ⟨δQ_s⟩^{αβ} ∝ |Γ^{αβ}_s|). At the peak the A1g channels are xx = yy (|.| = 20.1), zz (36.44) and
off-diagonal ≈ 0, as D3d symmetry requires ([z²] and [x²+y²] are A1g). Modes odd under inversion (Eu 25.45 meV, A2u 42.21 meV) are
numerically zero (S < 0.2 Å²/eV, i.e. < 0.3 % of the A1g value, from residual noise); the Raman-active Eg pair (25.59 meV) peaks at
5.80 eV with S = 37.4 / 37.6 Å²/eV (xz / yz channels), i.e. about half of the A1g peak. Below the direct gap (≈ 2.0 eV on the fine mesh)
the kernel is zero (1e-87) because only the pure-electronic resonance (Gaussian δ, η = 25 meV) is included.

## Cell (sealed, used verbatim) and internal coordinates

Lattice (Å, rows): a1 = (1.81950000, −3.15146644, 0), a2 = (1.81950000, 3.15146644, 0), a3 = (0, 0, 5.86800000) (a = 3.639 Å, c = 5.868 Å, P-3m1).
Positions (crystal): Sn (0,0,0); S (1/3, 2/3, 0.25418572); S (2/3, 1/3, 0.74581428). The relaxation of the internal coordinates at the
fixed cell (`run/01_relax`, forc_conv_thr 1e-4) converged in 0 BFGS steps: the total force at the given positions is 7e-5 Ry/bohr, so the
coordinates are unchanged. Residual stress at the sealed cell: 38.9 / 38.9 / 25.1 kbar (PBE wants a larger cell; the cell was not touched).

## Computational set-up

* Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (Sn: 4d10 5s2 5p2, S: 3s2 3p4), used scalar-relativistically (no SOC). ecutwfc = 80 Ry,
  ecutrho = 320 Ry (hints: Sn high 84 / normal 72 Ry; S 64 / 52). 26 valence electrons, 13 occupied bands, fixed occupations.
* SCF: 12x12x6 Γ-centred k-mesh, conv_thr 1e-12 (production run `run/12_nscf18/scf.in`). VBM = 6.8295 eV.
* DFPT at q = Γ (`run/03_ph/ph.in`): tr2_ph 1e-16, epsil = .true. (ε∞ = 8.72, 8.72, 6.60; Z*(Sn) = 4.92, 4.92, 1.92), dvscf saved for EPW.
  `dynmat.x` with asr = 'crystal' (`run/03_ph/dynmat.in`).
* NSCF for Wannier/EPW: full 18x18x9 grid (2916 k, explicit list in [0,1), nosym), 32 bands (`run/12_nscf18/nscf.in`).
  Band edges on this grid: VBM 6.8283, CBM 8.1345 eV. (A 12x12x6 model was built first; see convergence below.)
* Wannier (EPW step 1, `run/16_epw18/epw1.in`, Wannier90 input `run/16_epw18/out/sns2.win`): 10 WFs = Sn s, p + S p; bands 1–7
  (Sn 4d, S 3s) excluded; outer window [−1, 18] eV; frozen window [−1, 13.15] eV (= VBM + 6.32 eV; the first band outside the model,
  band 18, has its minimum at 13.32 eV on the coarse grid). Total spread 41.2 Å². vme = 'wannier', lpolar = .true., asr_typ = 'crystal'.
* Kernel (EPW step 2, `run/17_kernel18_k*/epw2.in`): lindabs = .true., photon grid 0.01–6.00 eV step 0.01 eV, degaussw = 0.025 eV
  (η of the SI "Methods"), ladsmear = .false., fsthick = 1e10 (all states), temps = 300 K (irrelevant for an insulator with fixed
  occupations), Fermi level read as 7.496 eV (mid-gap), fine q-mesh 1x1x1 (only q = Γ enters the kernel and the code zeroes its
  arrays per q), fine k-meshes 48x48x24 … 144x144x72 (aspect ratio of the reciprocal cell preserved). Only the Γ_c (triangle, pure
  electronic resonance) diagram is implemented in this build; the Γ_e term is "out of scope in v1" (declared only).

## Mesh convergence of the kernel (18x18x9 Wannier model; all files in `kernel/`)

| fine k-mesh | A1g peak: E (eV) | S (Å²/eV) | Eg peak: E (eV) | S (Å²/eV, mode 6 / 7) | time, 128 ranks |
|---|---|---|---|---|---|
| 48x48x24  | 5.44 | 77.49 | 5.81 / 5.80 | 37.53 / 37.59 | 2 min 22 s |
| 72x72x36  | 5.44 | 79.03 | 5.81 | 37.56 / 37.78 | 7 min 39 s |
| 96x96x48  | 5.46 | 77.82 | 5.79 | 37.95 / 38.10 | 16 min 06 s |
| 144x144x72 | 5.46 | 77.03 | 5.81 | 37.59 / 37.78 | 53 min 15 s |
| **192x192x96 (adopted)** | **5.46** | **77.19** | 5.80 | 37.43 / 37.61 | 1 h 14 min 40 s (2 nodes x 128 ranks) |

The peak position is stable at 5.44–5.46 eV (photon-grid step 0.01 eV) and the peak height changes by +2.0 %, −1.5 %, −1.0 %, +0.2 %
between successive meshes; the 144 → 192 change is 0.2 %, and the spectrum at 0.5 eV spacing agrees between 144 and 192 to ≤ 2 %
everywhere above the gap (`scripts/spectrum.py`), so the kernel is converged at the 1 % level. The peak is a smooth feature of
≈ 0.15 eV FWHM (values at 5.42/5.46/5.50 eV: 74.0 / 77.2 / 75.0 Å²/eV on 192x192x96), well resolved by the 0.01 eV grid.
The first 192 attempt on one node (128 pools of 27648 k) was killed out of memory (112 GB default allocation on `small`); the
production run used 2 nodes x 128 ranks with `--mem=200G` (`run/17_kernel18_k192/job.sh`).
Wannier-model sensitivity: the same 48x48x24 kernel with the 12x12x6 coarse model (`kernel/Gamma_alphabeta_s_48x48x24_coarse12x12x6model.dat`)
gives 81.3 Å²/eV at 5.44 eV (+5 % vs the 18x18x9 model); the 18x18x9 model is adopted as the better interpolation (below).

## Wannier interpolation quality (`run/16_epw18/out/bands_dft_vs_wannier.dat`, `scripts/compare_bands.py`)

DFT bands (pw.x `bands`, 281 k along Γ–M–K–Γ–A–L–H–A, `run/02_scf/bands.in`) vs EPW/Wannier interpolation along the same path
(`run/16_epw18/out/band.eig`), bands 8–17 (the 10 Wannier bands), DFT energies up to 12.9 eV = VBM + 6.07 eV (everything reachable by a
6 eV photon; DFT gap on the path 1.409 eV, VBM 6.831 eV, CBM 8.240 eV):

| set | N points | RMS (meV) | max (meV) |
|---|---|---|---|
| valence (bands 8–13, −0.33 … 6.83 eV) | 1686 | 3.79 | 40.0 |
| conduction (bands 14–17 up to 12.9 eV) | 864 | 5.41 | 44.3 |
| all | 2550 | 4.41 | 44.3 |

Per band: RMS 1.4 / 6.5 / 0.8 / 0.8 / 5.9 / 2.3 meV (valence bands 8–13) and 4.4 / 3.0 / 7.8 / 6.1 meV (conduction bands 14–17).
The maxima are isolated points at band crossings on the k_z = π/c plane (L–H), where the interpolated bands swap order; 1.3 % of the
points deviate by more than 20 meV. The 12x12x6 model gave RMS 5.4 meV (valence 4.1, conduction 7.3) and 1.8 % of points > 20 meV.
(DFT band energies are stored with 3 decimals, so the RMS floor is ≈ 0.3 meV.)

## Γ-point phonons (DFPT, `run/03_ph/out/ph.out`; ASR 'crystal' via dynmat.x, `run/03_ph/out/dynmat.log`)

| modes | ω (cm⁻¹) after ASR | THz | meV (EPW) | irrep (D3d) | activity |
|---|---|---|---|---|---|
| 1–3 | 0.00 (before ASR 3.2, 4.3, 4.3) | 0 | – | acoustic | – |
| 4–5 | 205.36 | 6.1565 | 25.4539 | Eu | IR |
| 6–7 | 206.42 | 6.1884 | 25.5857 | Eg | Raman |
| 8 | 311.73 | 9.3455 | 38.6486 | A1g | Raman |
| 9 | 340.48 | 10.2074 | 42.2116 | A2u | IR |

||dyn(ASR) − dyn(orig)|| = 1.7e-4; no LO–TO splitting at exactly q = Γ (as used by EPW). EPW's phonon frequencies at Γ reproduce these
(25.45, 25.59, 38.65, 42.21 meV in the kernel file header lines).

## Compute (`jobs.log`)

4.841 node-hours for the whole workflow (relax, DFPT, bands, two NSCF grids, two EPW Wannierizations, six kernel runs of which the
192x192x96 one cost 2.49; losses: one EPW step 1 of 0.5 node-hours in which Wannier90's frozen-window error left EPW hanging, and
0.025 node-hours for the out-of-memory 192 attempt). All production runs on LUMI-C `small`, chosen because `sbatch --test-only` predicted a much earlier start than `standard`.
Wall-clock: see RESULT.json (session start 2026-10-15 12:54 UTC; two interruptions by the model-account usage limit).

## Caveats

* PBE at the sealed (PBE-compressed) cell; no SOC; η = 25 meV Gaussian; only the pure-electronic-resonance diagram Γ_c of the kernel-variant build.
* Kernel values at the lowest photon energies use omegamin = 0.01 eV (ω = 0 would divide by zero in the i π/ω² prefactor); they are zero anyway below the gap.
* Degenerate Eg partners give slightly different channel sums (37.6 vs 37.8 Å²/eV) because the sum of |Γ^{αβ}| is not invariant under
  rotations inside the degenerate subspace; the A1g mode is non-degenerate and its invariant is unambiguous.
