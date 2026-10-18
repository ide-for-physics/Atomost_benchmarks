# REPORT — GaP_t1: light-induced coherent-phonon generation kernel Γ^{αβ}_s(ω_s; ω, −ω) from first principles

(cophon-bench v1 whiteboard, model fable. All numbers below are traceable to files in this folder; the headline numbers are
repeated in RESULT.json. Compute and wall time are at the end.)

## 1. Headline result

__HEADLINE__

## 2. System and sealed cell

- Cell used verbatim from `structure_POSCAR` / `structure.cif` (fcc primitive cell of zincblende GaP, a_conv = 5.44718 Å, V = 40.405 Å³;
  pw.x: alat 7.2787 bohr, V = 272.6787 bohr³). No cell relaxation (sealed).
  a1 = (0, 2.72358864, 2.72358864), a2 = (2.72358864, 0, 2.72358864), a3 = (2.72358864, 2.72358864, 0) Å.
- Ga at (1/4,1/4,1/4), P at (0,0,0) crystal. Both are fixed Wyckoff positions of F-43m (no free parameter): the SCF forces vanish
  identically (`remote_out/01_scf/scf_ph.out`: Total force = 0.000000), so no internal relaxation is needed or possible.
  Residual pressure at the sealed cell: 27.6 kbar (PBE at this lattice constant; not acted upon).
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (`Ga.upf`, 13 valence e: 3d10 4s2 4p1; `P.upf`, 5 e), used scalar-relativistically
  (no spin-orbit; allowed by the task). ecutwfc = 80 Ry (PseudoDojo "normal" hint for Ga), ecutrho = 320 Ry. 18 electrons, 9 occupied bands.
- PBE band edges (NSCF 12³, `remote_out/03_wan/nscf.out`): VBM 7.6368 eV (Γ), CBM 9.2301 eV (near X), indirect gap 1.593 eV.
  Ga-3d bands lie at ≈ −6.9 eV below the VBM (bands 1–5, excluded from the Wannier set).

## 3. DFPT phonons at Γ (acoustic sum rule)

Inputs: `inputs/02_ph/ph.in` (ph.x, 6×6×6 q-mesh = 16 irreducible q, epsil=.true., tr2_ph=1e-16, SCF on 8×8×8 k from `inputs/01_scf/scf_ph.in`),
`inputs/02_ph/q2r.in`, `matdyn.in`, `dynmat.in` (asr='crystal'), `dynmat_q001.in` (same, with q→0 along [001] for the non-analytic term).
Outputs: `remote_out/02_ph/` (ph.out, gap.dyn*, gap.fc, gap.freq, dynmat*.out).

| quantity | value | file |
|---|---|---|
| ε∞ (isotropic) | 11.2345 | ph.out |
| Z*(Ga), Z*(P) (before ASR) | +2.1403, −2.2444 | ph.out |
| ‖dyn(ASR) − dyn‖ | 1.27e−4 | dynmat.out |
| acoustic modes 1–3 at Γ after ASR | 0.0000 cm⁻¹ (|ν| < 1e−5 cm⁻¹; −2.7 cm⁻¹ before ASR) | dynmat_gamma.out |
| optical modes 4–6 at Γ (q = 0 exactly, no NAC): T2 (Γ15) triplet | 359.2545 cm⁻¹ = 10.7702 THz (×3), IR activity 5.17 (D/Å)²/amu | dynmat_gamma.out, dynmat.out |
| with the non-analytic term, q→0 ∥ [001] | TO 359.25 cm⁻¹ (10.7702 THz) ×2, LO 391.61 cm⁻¹ (11.7401 THz) | dynmat_gamma_q001.out |

Experiment for reference: TO(Γ) 365–367 cm⁻¹, LO(Γ) 403 cm⁻¹ (PBE at this cell underestimates by ~2 %, as expected).
The optical triplet at Γ transforms as T2 (= Γ15 = F2) of the point group T_d; it is simultaneously IR- and Raman-active.
The EPW kernel run evaluates the dynamical matrix at q = Γ exactly (the long-range part vanishes at q = 0), so the three optical modes
entering the kernel (imode = 4, 5, 6) are the degenerate T2 triplet at 10.770 THz (= 44.544 meV in the EPW output header).

## 4. Wannier interpolation quality

Coarse grids: NSCF 12×12×12 (explicit list of 1728 k in [0,1), nbnd = 40, `inputs/03_wan/nscf.in`), Wannier90 via pw2wannier90 (`inputs/03_wan/pw2wan_*.in`, `gap*.win`).
The DFT reference bands were computed with pw.x (`bands_wk_template.in`, nbnd 40, verbosity high) at exactly the 262 k-points of the
Wannier90 path L–Γ–X–W–K–Γ (bands_num_points = 60), so the comparison is point-by-point. Script: `scripts/compare_bands.py`.
Deviations are over all (k, band) pairs with E ≤ VBM (1048 points, bands 6–9) and CBM ≤ E ≤ CBM + 6 eV (899 points):

| set | projections (WFs) | frozen / outer window top (eV) | VB RMS / max (meV) | CB ≤ CBM+6 eV RMS / max (meV) | converged |
|---|---|---|---|---|---|
| B | Ga s,p,d + P s,p (13) | 16 / 26 | 12.5 / 76 | 38 / 286 | yes (Ga-d WFs delocalised) |
| D | Ga s,p + P s,p (8) | 14 / 22 | 1.8 / 10.8 | 108 / 887 (9.7 / 54 to CBM+4) | yes |
| E | Ga s,p,d + P s,p,d (18) | 16.5 / 40 | 2.2 / 10.9 | 7.2 / 44.7 | no (1000 it.) |
| **F (adopted)** | **Ga s,p + P s,p,d (13)** | **16 / 35** | **0.38 / 1.47** | **2.88 / 15.1** | **yes (271 it., Ω = 28.54 Å², max spread 2.71 Å²)** |
| G | Ga s,p,d + P s,p (13) | 16 / 35 | 1.4 / 6.0 | 4.8 / 26 | no (1000 it.) |

Set F sub-ranges: CBM..CBM+2 eV RMS 1.06 / max 4.3 meV; CBM..CBM+4 eV 1.24 / 6.4 meV; CBM..CBM+5 eV 1.83 / 14.0 meV.
The frozen window top (16.0 eV = CBM + 6.77 eV) covers the whole 0–6 eV photon range for transitions from the valence bands.
Data: `wannier_vs_dft_bands_setF.dat` (path coordinate, k, and E_DFT / E_W90 for the 13 bands), `wannier_vs_dft_stats_setF.txt`,
raw files `remote_out/03_wan/bands_wk.out`, `gapF_band.dat`, `gapF.wout`. The same set F (same windows, projections and
convergence settings) was re-Wannierised inside EPW (`inputs/04_epw/epw1_run2_wannierize.in`, job 22900599: Ω = 28.539 Å², converged) and the resulting
`gap.ukk` is what the production coarse run (`inputs/04_epw/epw1.in`, wannierize = .false.) and all kernel runs use. The DFT comparison of these EPW-side
Wannier bands (`remote_out/04_epw/gap_band.dat`, `gap.wout`) is `wannier_vs_dft_stats_epwF.txt`: VB RMS 0.41 / max 1.68 meV, CB ≤ CBM+6 eV RMS 2.92 / max 15.0 meV.

## 5. EPW kernel calculation

- Code: the authors' kernel variant (`EPW/src/indabs.f90`, `lindabs = .true.`): triangle diagram Γ_c with the velocity matrix
  elements h^α (vme = 'wannier'), the Γ-point e-ph matrix elements g^s interpolated from the 6×6×6 DFPT grid (lpolar = .true., ε∞ and Z* from ph.x),
  Gaussian electronic resonance of width degaussw = 0.025 eV (SI prescription, ladsmear = .false.), step occupations with the Fermi level fixed mid-gap
  (efermi_read, fermi_energy = 8.43 eV), all 13 Wannier bands active (fsthick = 20 eV). Output file: `Gamma_alphabeta_s.dat`
  (photon energy in eV; Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy in Å²/eV; one block per optical mode imode = 4..6).
- The code accumulates the kernel per fine q-point and writes it at the last q, so the fine q-mesh is Γ only (nqf = 1×1×1) and the
  k-mesh is the full (unreduced) fine mesh (mp_mesh_k = .false.; the tensor is not symmetrised by the code).
- Photon grid: omegamin = 0.01, omegamax = 6.0, omegastep = 0.01 eV (600 points; ω = 0 is excluded because of the 1/ω² prefactor).
- Inputs: `inputs/04_epw/epw1_run2_wannierize.in` (Wannierisation inside EPW), `inputs/04_epw/epw1.in` (coarse step: e-ph on 12³ k / 6³ q with the
  stored gap.ukk, writes gap.epmatwp), `epw2_template.in` → `epw2_k<N>.in` (fine step on N×N×N k, Γ q). Job scripts: `inputs/job4_epw1.sh`,
  `inputs/job5_epw_fine.sh` (48/72/96), `inputs/job6_epw_fine2.sh` (120/144), `inputs/job7_epw_fine3.sh` (192, 4 nodes).

__EPWSECTION__

## 6. Mesh convergence

__CONVERGENCE__

## 7. Compute and wall time

__COMPUTE__
