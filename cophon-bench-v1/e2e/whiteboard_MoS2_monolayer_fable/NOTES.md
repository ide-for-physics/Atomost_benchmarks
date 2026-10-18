# NOTES.md — running log (MoS2 monolayer, coherent-phonon kernel, cophon-bench v1 whiteboard)

Start: 2026-10-17T05:07 UTC (first command). Model: fable. Everything local lives in /home/wb/work; remote work in
`/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/MoS2_monolayer/fable_run/` (see "remote root" below).

## 1. Reading (05:07–05:25)
- Manuscript Eq. (Gamma_2nd_final): second-order kernel Γ^{αβ}_s(ω_s; ω, −ω) = diagram (c) [triangle: two optical vertices + EPC] + diagram (e)
  [optically perturbed EPC vertex g^{s;α}]. SI Sec. IV "Methods": η = 0.025 eV electronic broadening, PBE, SCF 1e-6 / phonon 1e-16 Ry;
  MoS2: 12x12x1 k and q coarse meshes, 90 Ry cutoff; amplitude ∝ |Γ^{αβ}_s|. The paper does not define an explicit "rotational invariant";
  the task sheet defines it as the per-mode magnitudes summed over Cartesian channels, so I use I_s(ω) = Σ_{αβ} |Γ^{αβ}_s(ω)| (9 channels)
  and ALSO report the Frobenius norm sqrt(Σ|Γ^{αβ}|²) and the diagonal trace in REPORT.md.
- Implementation note: EPW modifications (wan2bloch.f90, indabs.f90). Units: Å² / eV for tensorial kernels.
- Toolchain source (EPW/src/indabs.f90 of qe-phnlo-75), the authoritative definition of what this build computes:
  * The kernel is computed inside `indabs_main` (so `lindabs = .true.` triggers it), "v1 scope": Γ_c (triangle diagram) + Pi_0 only;
    `lgammae` exists in the namelist but is documented as "out of scope in v1" (no Γ_e term in this build). I therefore report the Γ_c kernel.
  * Gaussian deltas with width `degaussw` (= η; set to 0.025 eV as in the paper); 1/(ω_s + ε_ln + i·degaussw) propagator;
    optional adaptive smearing `ladsmear` (I keep the paper's fixed η: ladsmear = .false.).
  * Prefactor (iπ/ω²)/sqrt(2ω_s) · bohr2ang²/ryd2eV ⇒ output in Å²/eV. Division by ω² ⇒ ω = 0 gives NaN, so the photon grid starts at
    omegamin = omegastep = 0.01 eV, omegamax = 6.0 eV (600 points, 0.01 eV step; η = 25 meV is well resolved).
  * Output file `Gamma_alphabeta_s.dat`: for imode = 4..nmodes a header line "imode = N  ħω_s(meV)", then per photon energy (eV):
    Re,Im of xx, yy, zz, xy, xz, yz, yx, zx, zy.
  * Arrays are reset at every q and written at the last q ⇒ the fine q grid must be Γ only (nqf = 1x1x1). Bands: all `nbndfst` bands
    (fsthick window) enter, with occupation factors from `ef0` (use efermi_read with a mid-gap value).
  * EPW imposes the simple ASR on the coarse dynamical matrix (`dynmat_asr`), consistent with dynmat.x asr='simple'.
- Build quirks from the task sheet: diago_thr_init = 5e-6; npool = number of MPI ranks for EPW; explicit NSCF k list in [0,1).

## 2. Remote root
The remote root already contained an older directory tree (01_scf … 05_epw, owned by <user>, dated Oct 16) from somebody else's run.
I did not open or use any of it (task: work alone, from scratch). All my work is in the fresh sub-directory `fable_run/`.

## 3. Plan and key decisions
1. Cell: lattice vectors exactly from structure_POSCAR (ibrav = 0, CELL_PARAMETERS angstrom). Positions symmetrised to
   S z = ±0.0862217 (the POSCAR has 0.0862217 / 0.913778, i.e. a 3e-7 asymmetry) and then relaxed at fixed cell (allowed by the task).
2. Pseudopotentials: PseudoDojo nc-fr-04 PBE standard Mo.upf, S.upf used scalar-relativistically (no SOC). ecutwfc = 90 Ry
   (paper value; PseudoDojo hints Mo normal 80 / high 92 Ry).
3. Only q = Γ phonons are needed (Γ-point optical modes, EPW writes the kernel at the last q only). I run DFPT at Γ only
   (ph.x, ldisp with a 1x1x1 q-grid, tr2_ph = 1e-16, epsil = .true. for Born charges / dielectric tensor) and use a 1x1x1 coarse q-grid
   in EPW: the Wannier interpolation is then only in k, and g(k, q=Γ) at fine k is interpolated from the exact coarse-grid DFPT data.
   lpolar = .false. (no q-interpolation, nothing to correct). DFPT Γ frequencies with ASR from dynmat.x (asr = 'simple'; also gives irreps).
4. Coarse k mesh 12x12x1 (paper). NSCF on the full 144-point grid, nbnd = 40.
5. Wannier model chosen after looking at the DFT bands (target: valence + conduction to ~6 eV above the gap within a few meV).
6. Kernel: lindabs = .true., degaussw = 0.025 eV, fsthick large (all Wannier bands), efermi_read mid-gap, omegamin/omegastep = 0.01 eV,
   omegamax = 6 eV, fine meshes 96x96x1, 144x144x1, 192x192x1 (and larger if the budget allows) to show convergence of the peak.
7. Partitions: debug for < 10 min jobs, small/standard chosen by `sbatch --test-only` estimated start.

## 4. Log
- 05:07 UTC start. Read papers + toolchain source (see §1). Remote root already populated by someone else's run → using fresh `fable_run/`.
- 05:14 job A (fixed-cell relax + SCF, 12x12x1, 90 Ry) could not be submitted to `debug`: the shared user already has 2 debug jobs
  (other benchmark arms: bos_*). `sbatch --test-only`: small → start ~13:20 EEST (5 h), standard → next day. Submitted the 64-core
  variant to `small` (job 22926969) as a fallback and I am polling (every 120 s, remote wait script) for a free debug slot.
- Wrote inputs for job B (ph.x at Γ, 1x1x1 q grid, epsil, tr2_ph 1e-16; dynmat.x asr no/simple/crystal; save/ for EPW),
  job C (bands on Γ-M-K-Γ 165 points + NSCF 144-point grid, nbnd 40), EPW templates, and the analysis scripts (inputs/tools/).
- 05:23 job A ran on debug (22927057, 13 s). The given structure is already at equilibrium: total force 8.8e-5 Ry/Bohr < forc_conv_thr,
  BFGS made 0 steps ⇒ positions unchanged (Mo 2/3,1/3,0; S 1/3,2/3,±0.0862217). PBE gap 1.657 eV (VBM −0.4609, CBM 1.1959 eV,
  mid-gap 0.3675 eV used as EPW Fermi level). 12 symmetry operations (D3h).
- 05:26 job BC (22927068, 3:04): ph.x at Γ (6 irreps) in 64 s. Frequencies (cm-1) without ASR: 1.3, 5.5, 5.5 (acoustic), 276.48 (E''),
  373.43 (E'), 396.64 (A1'), 458.42 (A2''); with asr='simple' (dynmat.x): 0, 0, 0, 276.44, 276.44, 373.39, 373.39, 396.65, 458.42
  (irreps from the dynmat/ph.x symmetry analysis: E'' (Raman), E' (IR+Raman), A1' (Raman), A2'' (IR)). ε∞ = 5.79 (in-plane, slab average),
  Z*(Mo) = −0.99 (in-plane). NSCF: bands 1–4 Mo 4s4p (−61/−35 eV), 5–6 S 3s (−14.5…−12.3), 7–13 valence p–d manifold (−6.21…−0.46),
  14–17 conduction d manifold (1.196…4.38), band 18 starts at 4.92 eV ⇒ bands 7–17 are an isolated 11-band group.
- Wannier model decision: 11 WFs (Mo:d, S:p) on the isolated group (exclude_bands 1-6,18-40; no disentanglement needed). This covers
  all resonant transitions for ħω ≤ 5.38 eV (= band-18 minimum − VBM) and all valence→conduction pairs of the d/p manifold; bands ≥ 18
  (nearly-free-electron / Mo 5s-like, ≥ 3.7 eV above the CBM) are outside the model. A larger (SCDM) model is kept as an optional stage 2.
- 05:32 job D (22927108, 1:54 on 48 ranks): wannier90 converged, spreads 1.5–1.8 Å² (Ω_tot 18.6 Å²), EPC decay |g(R_e≈20 Å)| ~ 2e-5 Ry.
  DFT vs EPW-interpolated bands on the identical 165-point Γ-M-K-Γ path: valence RMS 0.33 meV / max 1.26 meV; conduction (to 4.6 eV)
  RMS 0.42 meV / max 1.74 meV (wannier/bands_dft_vs_wannier11.dat, compare_bands.py).
- Kernel runs: separate directories 05_kernel/k<N> (EPW writes its outputs in cwd), epwread from the 04_epw Wannier data; meshes
  48, 96, 144, 192 first (one debug job, sequential), then 288/384.
- 05:38 first kernel job failed immediately: relative outdir '../03_nscf/tmp' is wrong one level deeper (k<N>/) → MPI_FILE_OPEN error on
  mos2.epmatwp. Fixed to '../../03_nscf/tmp' (and '../../02_ph/save'); resubmitted (22927159).
- 05:45 kernel meshes done (22927159; 11 s / 37 s / 59 s / 101 s for 48/96/144/192 on 128 ranks). EPW phonon energies (ASR applied):
  34.274 (E''), 46.295 (E'), 49.178 (A1'), 56.837 (A2'') meV. Peak of I_sum = Σ_ab |Γ^ab_s| between 0 and 6 eV: mode 8 (A1', 49.178 meV
  = 11.891 THz) at ħω = 2.83 eV: 93.78 / 91.432 / 91.448 / 91.449 Å²/eV (48/96/144/192) → converged to < 0.02 % from 96x96 on.
  At the peak Γ^xx = Γ^yy = 20.67 + 40.74 i (|.| = 45.68), all other channels < 0.05 (A1' ⇒ isotropic in-plane, no zz coupling
  to in-plane light... zz ~ 0.02). Frobenius norm at the peak 64.59; trace 91.33. E' modes 6/7 peak at 2.90 eV with I_sum ≈ 29.5
  (xx = −yy / xy = yx pattern as required by symmetry); E'' (4,5) and A2'' (9) are ≲ 5 Å²/eV (symmetry-forbidden at first order).
- 05:50–06:01 meshes 288 (22927219, 3:56) and 384 (22927253, 6:36): peak identical to 192 to 7 digits (91.44932 Å²/eV at 2.83 eV).
  Convergence is exponential (smooth Gaussian-broadened integrand): 48→96 −2.5 %, 96→144 +1.8e-4, 144→192 +1.1e-5, 192→288→384 < 1e-7.
  Adopted mesh for the deliverable: 384x384x1 (finest computed); all coarser files kept as kernel/Gamma_alphabeta_s_<mesh>.dat.
- 06:07 stage 2 (job 22927321, after a first try that stopped because EPW requires auto_projections=.true. with scdm_proj): SCDM-erfc
  (μ = 7 eV, σ = 2 eV), 20 WFs from bands 7–40 in [−7, 12] eV, frozen to 7 eV. Spreads 1.6–11 Å² (Ω_tot 120 Å²: the states above the
  d manifold, bands ≥ 18, are nearly-free-electron-like and delocalised). Interpolation quality on the Γ-M-K-Γ path: valence RMS 41 meV
  / max 373 meV, conduction (to 7 eV) RMS 10 meV / max 50 meV — far from "a few meV". Decision: NOT adopted; the 11-WF isolated-group
  model (sub-meV) stays the production model. The SCDM model is only used for a sensitivity check of the kernel peak (k96 run,
  job 22927417) to quantify the effect of bands 18–26 as intermediate/final states.
- 06:12 SCDM-20 kernel (96x96x1, 2:00): same peak position and mode (A1', 2.83 eV), I_sum = 80.0 Å²/eV vs 91.4 with the 11-WF model
  (−12 %). The SCDM result also violates the A1' symmetry (|Γ^xy| = 2.3 = 6 % of |Γ^xx|; xx ≠ yy by 1 %), so a good part of the
  difference is interpolation artefact rather than physics; the extra bands change the peak by ≲ 10 %. One more extended model is
  tried (job 22927444): 15 projections Mo:s,p,d + S:p, frozen window to 6 eV, outer window to 10.5 eV (bands 7–21 everywhere).
- 06:18 15-projection model (3:50): the three extra WFs have spreads 11–20 Å²; valence RMS 27 meV / max 171 meV, conduction (to 6 eV)
  RMS 24 meV / max 222 meV. Also not acceptable. Final decision: production = 11-WF isolated-group model (sub-meV interpolation),
  which covers all optical transitions for ħω ≤ 5.38 eV; the states above the d manifold (bands ≥ 18, NFE-like) cannot be Wannierised
  to meV accuracy on a 12x12 coarse grid and shift the peak by ≲ 10 % when (imperfectly) included.
- Production kernel file: 384x384x1 mesh (identical to 192 and 288 to 7 digits). Clean-up of wavefunctions and the test outdirs follows.
- 06:19 cleanup on LUMI: deleted my wavefunction files (01_scf/tmp, 03_nscf/tmp, tmp_bands) and the test outdir tmp_scdm
  (3.6 GB + 2.8 GB → 60 MB); kept mos2.epmatwp, save/, *.fmt, all inputs/outputs. Downloaded every used input/output to remote_files/.
- Band-edge check on the DFT path: VBM at Γ (−0.4610 eV), K valence top 19 meV lower (−0.480); CBM at K (1.1960); indirect gap 1.657,
  direct K gap 1.676 eV (scalar-relativistic PBE at a = 3.1856 Å).
- 06:22 wrote RESULT.json (peak 2.83 eV, 91.44932 Å²/eV, mode 8 A1' 11.8913 THz, mesh 384x384x1, 0.5119 node-hours), REPORT.md, DONE.
  Total compute 0.51 of 20 node-hours; wall 1.27 h.

## 5. Open points / what I would do with more time
- Γ_e (diagram e) is not available in this build ("v1 scope"); the kernel is Γ_c.
- A Wannier model that includes the NFE conduction states above 4.4 eV with meV accuracy would need a denser coarse k grid (e.g. 24x24x1)
  or a different basis; with 12x12x1 the SCDM / extra-projection attempts give 25–40 meV RMS errors and were rejected. Their kernel
  (SCDM test) changes the peak by −12 % (upper bound, includes artefacts), position and mode unchanged.
- SOC was not included (allowed by the task sheet).
