# REPORT — GaP_t1: light-induced coherent-phonon generation kernel Γ^{αβ}_s(ω_s; ω, −ω) from first principles

(cophon-bench v1 whiteboard, model fable. All numbers below are traceable to files in this folder; the headline numbers are
repeated in RESULT.json. Compute and wall time are at the end.)

## 1. Headline result

| quantity | value | source |
|---|---|---|
| peak photon energy of the largest invariant M_s(ω) = Σ_αβ |Γ^αβ_s(ω)| in 0–6 eV | **2.82 eV** | `kernel/Gamma_alphabeta_s.dat` (144x144x144), `scripts/make_result.py` |
| its value (per-mode magnitude summed over the 9 Cartesian channels) | **20.960 Å²/eV** | same |
| dominant phonon mode | **10.7705 THz** (44.543 meV), irrep **T2** (Γ15, triply degenerate TO/LO optical triplet of zincblende; imode 6 of the file) | kernel file header; `remote_out/02_ph/dynmat_gamma.out` |
| adopted fine k-mesh | **144x144x144** (Γ-only q) | `inputs/04_epw/epw2_template.in` |
| compute | **5.18 node-hours** | `jobs.log` |
| wall time (container start 2026-10-15T09:26Z → DONE) | **35.5 h** (two interruptions by the model-account usage limit: 10-15 13:38Z→10-16 10:11Z and 10-16 13:15Z→17:07Z are included) | transcript time stamps |

Invariant convention (decided, see NOTES.md §4): for each optical mode s the rotational invariant is the per-mode magnitude M_s(ω) = Σ_{αβ} |Γ^{αβ}_s(ω_s; ω, −ω)| over the nine Cartesian channels (complex modulus of each channel); the reported peak is the maximum of M_s over the optical modes and over the photon grid 0.01–6.00 eV, and the reported mode is the one realising that maximum (it is also the mode with the largest M_s at that energy). Because the three optical modes are an exactly degenerate T2 triplet, the individual M_s depend on the basis EPW's diagonaliser picks inside the degenerate subspace; the triplet sum Σ_s M_s and the fully invariant Frobenius norm √Σ_s Σ_αβ |Γ|² are therefore also tabulated in §6.

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

Fine runs (`remote_out/04_epw/k<N>/epw2_k<N>.out`): epwread from `epwdata.fmt`, `vmedata.fmt`, `03_wan/tmp/gap.epmatwp` (8.9 GB) written by the coarse run (`remote_out/04_epw/epw1.out`, 128 MPI ranks = pools, 40.7 min). The coarse run reads the ph.x irreducible-q order from `gap.dyn0` (authors' patch; without it EPW mis-assigns the dvscf files, which crashed the first attempt), the converged set-F Wannier functions from `gap.ukk`, and evaluates 216 coarse q with the polar long-range correction. Every fine run gives identical mode energies 44.5434 meV (×3) in the file header. The code also writes `Pi_0.dat` (field-free phonon self-energy) and `epsilon2_*` absorption files, which are not used here.

## 6. Mesh convergence

Kernel files: `kernel/Gamma_alphabeta_s_<mesh>.dat` for every mesh and `kernel/Gamma_alphabeta_s.dat` = the adopted 144x144x144 file (byte-identical copy of `remote_out/04_epw/k144/Gamma_alphabeta_s.dat`). Script: `scripts/mesh_convergence.py`.

| fine k-mesh | peak photon energy (eV) | max_s M_s (Å²/eV) | mode (imode) | Σ_s M_s over the T2 triplet (Å²/eV) | Frobenius ‖Γ‖ (Å²/eV) | M_4, M_5, M_6 at the peak |
|---|---|---|---|---|---|---|
| 48×48×48 | 2.88 | 20.374 | 6 | 57.43 | 16.912 | 17.04, 20.02, 20.37 |
| 72×72×72 | 2.83 | 21.143 | 6 | 59.60 | 17.565 | 17.69, 20.77, 21.14 |
| 96×96×96 | 2.82 | 20.555 | 6 | 57.95 | 17.089 | 17.19, 20.21, 20.56 |
| 120×120×120 | 2.82 | 20.731 | 6 | 58.45 | 17.236 | 17.34, 20.38, 20.73 |
| **144×144×144** | **2.82** | **20.960** | 6 | 59.10 | 17.427 | 17.53, 20.61, 20.96 |

Differences between consecutive meshes of the triplet-summed spectrum S(ω) = Σ_s M_s(ω) (RMS over 0–6 eV relative to the mean of S; max relative to the peak):

| meshes | RMS ΔS / ⟨S⟩ (0–6 eV) | max ΔS / max S | RMS ΔS / ⟨S⟩ (2.5–3.5 eV) | peak max_s M_s change |
|---|---|---|---|---|
| 48³ → 72³ | 35.1 % | 26.7 % | 22.0 % | +3.78 % |
| 72³ → 96³ | 20.7 % | 17.7 % | 11.9 % | -2.78 % |
| 96³ → 120³ | 13.6 % | 11.9 % | 6.8 % | +0.85 % |
| 120³ → 144³ | 9.6 % | 9.7 % | 4.4 % | +1.11 % |

The peak is the E1 critical point of GaP: the top valence bands (bands 8, 9) and the first conduction band run parallel along the whole Λ line L→Γ, with a PBE direct transition energy of 2.80 eV at L and 2.81–2.83 eV along Λ (`wannier_vs_dft_bands_setF.dat`; the PBE direct gap at Γ is only 1.84 eV and the Γ E0 transitions give the weak onset near 2.0 eV). This two-dimensional van Hove singularity makes the peak sharp and already stable in position and height from 72³ onwards, while the broad plateau above 3 eV and the weak features at 4–5 eV need the denser meshes because the 25 meV Gaussian is narrower than the fine-mesh energy spacing of the coarser grids.

## 7. Compute and wall time

Total from `jobs.log` (node = 128 cores; shared-node jobs counted as cores × hours / 128): **5.18 node-hours** of the 20 allowed.

```
22864934 | SCF 8^3 (DFPT), SCF 12^3, bands path, NSCF 12^3 nbnd=40 | small | 32 cores x 0:01:24 = 0.006 nh
22864935 | DFPT ph.x 6x6x6 q (16 irr. q), epsil | small | 64 cores x 0:27:45 = 0.231 nh
22865421 | Wannier projection tests B/C (pw2wannier90+wannier90) + DFT bands at W90 path k | small | 32 cores x 0:25:32 = 0.106 nh
22867643 | Wannier round 2 (failed: NSCF wfcs overwritten) + phonon post-proc (gather save/, q2r, matdyn, dynmat) | small | 32 cores x 0:01:43 = 0.007 nh
22868808 | NSCF rerun + Wannier round 2 (D done; E timed out, F/G not run) | small | 32 cores x 1:30:22 = 0.377 nh
22873311 | Wannier round 3 (sets E/F/G concurrently) | small | 32 cores x 0:58:33 = 0.244 nh
22899917 | EPW coarse (Wannierise set F OK; crashed reading save/gap.dyn_q5 at irr. q #5) | small | 64 cores x 0:15:08 = 0.126 nh
22899941 | EPW fine meshes (started after the crashed J4 because its script exited 0; died at once: no crystal.fmt) | small | 128 cores x 0:00:10 = 0.004 nh
22900599 | EPW coarse rerun with gap.dyn0 (Wannierise set F OK, all 216 q done; OOM-killed in the Bloch->Wannier step: small gave only 56 GB for 64 cores) | small | 64 cores x 1:15:18 = 0.628 nh
22900600 | EPW fine meshes, afterok:22900599 -> never started (DependencyNeverSatisfied), cancelled | small | 0 nh
22918065 | EPW coarse (reads gap.ukk; e-ph on 12^3 k / 6^3 q with dyn0 ordering; Bloch->Wannier; writes gap.epmatwp 8.9 GB) OK | small | 128 cores x 0:40:42 = 0.678 nh
22918066 | EPW fine kernel runs k=48^3 (3.3 min), 72^3 (11.5 min), 96^3 (29 min); q=Gamma; afterok:22918065 | small | 128 cores x 0:44:04 = 0.734 nh
22919387 | EPW fine kernel runs k=120^3 (45 min) and 144^3 (77 min); q=Gamma; afterok:22918066 | small | 128 cores x 2:02:20 = 1.953 nh
22920338 | EPW fine kernel k=192^3 on 4 nodes (512 ranks): OOM at start-up (1.85 GB/rank of full-mesh arrays; not feasible with this build) | small | 4 nodes x 0:01:17 = 0.086 nh
```

Wall time: container start 2026-10-15T09:26Z to DONE 2026-10-16T20:54Z = 35.5 h, of which ~24.6 h were the two usage-limit interruptions of the model account (no compute ran during the first; the OOM-killed coarse job 22900599 ran during the second).
