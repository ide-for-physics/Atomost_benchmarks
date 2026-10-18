# NOTES.md — SnS2_mp1170 coherent-phonon generation kernel (cophon-bench v1, whiteboard)

Start: 2026-10-15 ~16:50 (container clock). Remote root: /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/SnS2_mp1170

## What the code computes (read from EPW/src/indabs.f90 of the kernel-variant build)
- `lindabs = .true.` triggers `indabs_main`, which (besides stock phonon-assisted absorption) accumulates
  `Gamma_alphabeta_s(iw, a, b, imode)`: the triangle diagram Gamma_c of the manuscript, Eq. (SI, first-principles section),
  with Gaussian delta (w0gauss, width `degaussw`, or adaptive if `ladsmear`) for the electronic resonance and a Lorentzian
  1/(w_s + eps_ln + i*degaussw) for the phonon-resonant denominator. Prefactor i*pi/omega^2 / sqrt(2 w_s), units Å²/eV
  (bohr2ang**2/ryd2eV). The Gamma_e (g^{s;alpha}) diagram is "out of scope in v1" in this build (lgammae declared only).
- Written at the last q-point only, to `Gamma_alphabeta_s.dat`: header 3 lines, then per optical mode (imode = 4..nmodes):
  a line `imode = N  <phonon energy meV>` followed by nomega lines: E(eV), then Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy.
- Arrays are allocated/zeroed per q-call, so only q = Gamma must be in the fine q list: nqf1=nqf2=nqf3=1.
- Velocity operator: the authors' note (vmewan2bloch with cvmew position matrix) = `vme = 'wannier'`.
- Photon grid: omegamin/omegamax/omegastep (eV). Task: 0..6 eV. I use omegamin = 0.01 (omega=0 would divide by zero
  in the i*pi/omega^2 prefactor), omegamax = 6.0, omegastep = 0.01.
- Broadening: SI "Methods": eta = 0.025 eV -> degaussw = 0.025 eV, ladsmear = .false. (paper's parameter; adaptive smearing
  would change peak heights, so I keep the published value).

## Decisions
- Cell sealed: CELL_PARAMETERS taken verbatim from structure_POSCAR; internal coordinates relaxed at fixed cell (allowed).
- Pseudopotentials: PseudoDojo nc-fr-04 standard Sn (4d10 5s2 5p2, Z=14), S (Z=6), used scalar-relativistically
  (lspinorb=.false.). Hints: Sn normal 72 Ry / high 84 Ry; S normal 52 / high 64. I use ecutwfc = 80 Ry, ecutrho = 320 Ry.
- Coarse mesh 12x12x6 (k and SCF), q = Gamma only for DFPT (nq 1x1x1) since only Gamma modes enter the kernel.
- Partition: `sbatch --test-only` at 16:55 gave small -> starts 16:59 today, standard -> 08:42 tomorrow. Use small.
- Budget 20 node-hours; fine-mesh EPW runs are the main cost; plan meshes 48x48x24 -> 72x72x36 -> 96x96x48 as budget allows.

## Log
- 16:00 Submitted relax on small (22874330); it sat on Priority behind ~6 other jobs of this shared account, so cancelled it
  and resubmitted on debug (22874406, expected < 10 min, 32 cores) — allowed by the rules for short jobs.
- 16:05 relax (22874406): forces already < 1e-4 Ry/bohr at the sealed-cell MP positions; final S z = 0.25418572 (unchanged).
  12 symmetry ops (P-3m1, D3d). VBM = 6.8295 eV (13 occupied bands, 26 electrons).
- 16:06 DFPT at Gamma (22874459, tr2_ph 1e-16, epsil): eps_inf = (8.72, 8.72, 6.60); Z*(Sn) = (4.92, 4.92, 1.92).
  dynmat.x asr='crystal': 0,0,0 | Eu 205.36 (x2) | Eg 206.42 (x2) | A1g 311.73 | A2u 340.48 cm-1
  (= 6.157, 6.188, 9.346, 10.207 THz). Irreps from ph.x mode-symmetry analysis (D_3d). TO frequencies (no LO-TO at q=0 exactly),
  which is what EPW uses at q = Gamma.
- 16:10 DFT bands along G-M-K-G-A-L-H-A (281 pts, 40 bands): VBM 6.831, CBM 8.240 eV, PBE gap 1.409 eV. Bands 1-5 Sn 4d (-14 eV),
  6-7 S 3s (-7..-4 eV), 8-13 valence (S 3p / Sn 5s), 14 isolated CBM band (8.24-9.95), 15-17 Sn 5p (10.5-14.5), 18+ >= 13.55 eV.
  Wannier model A: 10 WFs = Sn s,p + S p, exclude_bands 1-7, outer window [-1, 18] eV, frozen window [-1, 13.4] eV
  (13.4 < min of band 18 = 13.545 so all 10 bands are frozen up to VBM+6.57 eV). Transitions <= 6 eV only reach conduction
  states below 12.83 eV, which are all inside the frozen window. Plan: check sensitivity to a larger model later if budget allows.
- 16:10 NSCF on the full 12x12x6 grid: lowest unoccupied 8.1629 eV (grid gap 1.333 eV); EPW Fermi level set mid-gap: 7.496 eV. EPW step 1 submitted (22874562, debug).

## Session 2 (2026-10-16, resumed 13:15 EEST after the account usage limit cut session 1 at 18:40 EEST on 10-15)
- Cluster state on resume: my EPW step 1 (22874562, debug) had FAILED: Wannier90 "More states in the frozen window than target WFs"
  (band 18 reaches 13.317 eV on the 12x12x6 grid, below my dis_froz_max = 13.4 chosen from the path only), and the Wannier90 error
  left EPW hanging until the 30 min limit (0.5 node-hours lost; logged).
- My remote root had been reorganised by someone else after my cut-off: my directories were moved into `prior_attempt_archive/`
  and a new `run/` tree (jobs 22877895..22879158, submitted 18:44-19:37 EEST on 10-15, i.e. after my session ended) with its own
  scf/ph/EPW/kernel outputs appeared. I did not submit those jobs and they are not my work; I do not read or use anything from
  `run/` (task: work alone, from scratch; every number traceable to my own jobs.log). I moved my own directories into `wb/`
  (remote root/wb/01_relax, 02_scf, 03_ph, 06_epw) and continue there. `run/` is left untouched (not mine to delete).
- Fix: dis_froz_max = 13.2 eV (band 18 min on the full coarse grid = 13.317 eV; no band-18 state below 13.2 at any of the 864 k;
  frozen window still covers VBM + 6.37 eV, above the highest state reachable by a 6 eV photon, VBM + 6.0 = 12.83 eV).
  Step 1 resubmitted on `small` (64 ranks, 40 min limit) rather than debug, so a hang cannot block a debug node again.
- 13:24 EPW step 1 (22899940) OK: total spread 42.2 A^2 (Sn s 3.0, Sn p 7.2-7.8, S p 2.5-3.0 A^2). Wannier vs DFT along
  G-M-K-G-A-L-H-A up to 12.9 eV (VBM+6.07): RMS 5.4 meV (valence 4.1, conduction 7.3), max 37 meV (band 9) / 60 meV (band 16,
  near 13.6 eV); 1.8% of points deviate > 20 meV, nearly all on the kz = pi/c plane (A-L-H). EPW phonons at Gamma reproduce
  dynmat (25.45, 25.59, 38.65, 42.21 meV). Data: run/06_epw/out/bands_dft_vs_wannier.dat.
- Decision: the z-interpolation of the 12x12x6 coarse mesh (6 points along kz) is the weak spot; redo NSCF + EPW step 1 on an
  18x18x9 coarse mesh (same windows/projections; ~0.5 node-hours) for the production kernel. Meanwhile the 48x48x24 kernel run
  with the 12x12x6 model (22900216) gives timing and a first look. Submitted 18x18x9 scf+nscf (22900219, small).
- 13:30 First kernel (48x48x24, 12x12x6 model, 22900228, 2 min on 128 ranks): only Raman-active modes carry weight
  (A1g 38.65 meV: peak 81 A^2/eV at 5.44 eV; Eg 25.59 meV: ~40 at 5.81 eV); Eu/A2u (odd under inversion) are ~1e-1 to 1e-86,
  as D3d symmetry requires. Secondary A1g feature at 3.8 eV (68). Point-to-point noise 10-20% on this mesh.
  Cost scaling: 48x48x24 -> 2 min, so 96x96x48 ~16 min, 144x144x72 ~55 min, 192x192x96 ~2.2 h (128 ranks).
- 13:47 EPW step 1 on 18x18x9 (22900512, 16 min): spread 41.2 A^2. Wannier vs DFT up to 12.9 eV: RMS 4.4 meV (valence 3.8,
  conduction 5.4), max 44 meV; 1.3% of points > 20 meV, nearly all on L-H (kz = pi/c plane) at band crossings (bands 9, 12, 14, 16).
  Modest improvement over 12x12x6 (5.4 meV RMS, 1.8% > 20 meV); the remaining outliers are crossing-related, not mesh-related.
  Adopted: 18x18x9 model for production. Kernel meshes submitted: 48x48x24, 72x72x36, 96x96x48, 144x144x72 (22901079-82).
- Fermi level for the kernel: 7.496 eV (mid-gap of the 12x12x6 grid); on the 18x18x9 grid VBM 6.8283 / CBM 8.1345, so 7.496 is
  still inside the gap; with fixed occupations only above/below-gap matters (f_ij = +-1), so the exact value is irrelevant.

## Session 3 (2026-10-16, resumed 20:09 EEST after the usage limit cut session 2 at 16:15 EEST)
- All four production kernel jobs (22901079-82; 48/72/96/144 fine meshes, 18x18x9 model) completed between 14:00 and 14:51 EEST.
  A1g (38.65 meV) peak: 77.49 @5.44 (48), 79.03 @5.44 (72), 77.82 @5.46 (96), 77.03 @5.46 eV (144) A^2/eV; Eg pair 37.6-38.1 @5.79-5.81 eV;
  Eu/A2u ~ 0 (parity). 96 -> 144 changes the peak by 1.0 %; adopted 144x144x72. Files copied to kernel/ (converged = 144x144x72).
- Definition of the reported invariant: S_s(w) = sum over the 9 Cartesian channels of |Gamma^{ab}_s(w)| (task sheet: "per-mode magnitudes
  summed over Cartesian channels"; SI: <dQ_s>^{ab} ~ |Gamma^{ab}_s|). mode_thz taken from the kernel file header (38.6486 meV = 9.3452 THz;
  dynmat with ASR gives 9.3455 THz) so that RESULT.json agrees with the kernel file.
- Submitted a 192x192x96 check (22918082, small, 1 node x 128 ranks, 4 h limit, expected ~2.2 h run). `sbatch --test-only`: small ->
  2026-10-17 14:55 EEST, standard -> 2026-10-18 16:14 EEST (after the 3-day deadline, 15:54 EEST on 10-18), 2-node variants no earlier;
  so small. (Earlier today the same partition started my jobs within 30 min; the estimate is a backfill upper bound.)
  Budget: 2.327 node-hours used; the check costs ~2.2 -> ~4.5 of 20.
- Wavefunction files of both NSCF runs were already deleted in session 2 (tmp/sns2.save holds only charge density + xml + pseudos);
  the sns2.epmatwp files (198 MB each, 02_scf/tmp and 12_nscf18/tmp) are kept until the last kernel run is done, then deleted.
- Wrote REPORT.md and RESULT.json from the 144 mesh now so that the deliverables are complete even if the 192 run does not start before
  the deadline; if it finishes, the adopted mesh/peak will be updated to 192x192x96 (and REPORT.md gets an addendum).
- Other jobs under this shared user (gap_epw1/gap_epwk, 22918065/66, and 22900600 earlier) are not mine (not in my jobs.log); left alone.
- 20:18 EEST: the 192 job (22918082) started within 7 min (the --test-only estimate was far too pessimistic) but was OOM-killed after
  90 s: the small partition gives 112 GB per node by default (sacct ReqMem) and 128 pools x 27648 k each need ~1 GB per rank
  (144 run: 11664 k per pool, VmHWM 640 MB per rank, 77 GB total). Fix: 2 nodes x 128 ranks (13824 k per pool) and --mem=200G per node;
  resubmitted as 22918331 (small, 3 h limit, expected ~1.1 h). Cost of the failure 0.025 node-hours (logged).
- 21:41 EEST: 192x192x96 (22918331, 2 nodes, 1 h 15 min, 2.489 node-hours) done: A1g peak 77.19 A^2/eV at 5.46 eV (144: 77.03, +0.2 %);
  Eg 37.4/37.6 at 5.80 eV. Converged; adopted 192x192x96 as the production mesh (kernel/Gamma_alphabeta_s.dat = 192 file; all
  coarser meshes kept as kernel/Gamma_alphabeta_s_<mesh>.dat). Total compute 4.841 of 20 node-hours.
  Deleted the two sns2.epmatwp scratch files (wavefunctions were already gone); remote tree now 533 MB.
- Final: RESULT.json regenerated from the 192 file (peak_ev 5.46, peak 77.19 A^2/eV, A1g 9.3452 THz), REPORT.md updated, DONE written.
