# NOTES.md — Bi2O2Se coherent-phonon kernel (cophon-bench v1, whiteboard)

Start: 2026-10-17 ~04:10 UTC (container clock). Operator: Claude (fable), alone.

## 0. Reading / reconnaissance (04:10–04:40)
- Papers: Manuscript (Hu, Guo, Li, Wang, Chang), SI, implementation note. The target is the second-order
  light-induced coherent-phonon generation kernel Gamma^{ab}_s(omega_s; omega, -omega), SI Sec. "First-principles
  calculation": Gamma = Gamma|_c (triangle diagram, three-band) + Gamma|_e (covariant-derivative-of-EPC vertex).
  Electronic broadening eta = 0.025 eV in the paper; isotropic field assumed; amplitude ~ |Gamma^{ab}_s|.
- Toolchain on LUMI: `/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75` (QE 7.5 + modified EPW).
  Read `EPW/src/indabs.f90`: the kernel is accumulated in `indabs_main` (so it needs `lindabs = .true.`),
  for q = Gamma only (one call per q-point, arrays zeroed each call, written at the last q-point) into
  `Gamma_alphabeta_s.dat` (header: photon energy (eV), then Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy in Ang^2/eV,
  one block per mode with the mode energy in meV). In THIS build only the triangle term Gamma|_c (+ Pi_0) is
  implemented ("Gamma_e / Pi_kernel (epvf17) are out of scope in v1" in the source); the input flag `lgammae`
  exists in the namelist but has no consumer in `use_wannier.f90`/`indabs.f90` of this port, so the delivered
  kernel is Gamma|_c. `ladsmear` (adaptive smearing) exists; I keep the paper's fixed eta = degaussw = 0.025 eV.
  The kernel uses vmef (needs `vme='wannier'`), epf17, etf, the Fermi level ef0 (use `efermi_read` + mid-gap
  `fermi_energy`), bands within `fsthick` of ef0, Gaussian deltas of width degaussw on the photon grid
  omegamin..omegamax step omegastep, acoustic modes skipped by `eps_acoustic`.
  Cartesian tensor components are accumulated without symmetrization -> the fine mesh must be the full BZ
  (mp_mesh_k = .false.).
- Remote root already contained files from an earlier attempt (dated 2026-10-16, dirs kern32/fin64/wv1...). Rule says
  "from scratch": I did not open them and I work in a fresh subdirectory `fable/` of the root.
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (Bi-d, O, Se-d), used scalar-relativistically (no SOC,
  QE averages the j components). Hints (normal/high): Bi 66/74, O 84/96, Se 86/98 Ry -> ecutwfc = 90 Ry.
- Crystal: I4/mmm Bi2O2Se, sealed bct primitive cell a1=(-a/2,a/2,c/2), a2=(a/2,-a/2,c/2), a3=(a/2,a/2,-c/2),
  a = 3.92939 Ang, c = 12.41260 Ang (exactly the Setyawan-Curtarolo BCT convention, so SC k-labels apply directly).
  Centrosymmetric: D4h. Gamma modes: A1g + B1g + 2Eg (Raman) + 2A2u + 2Eu (IR) optical, A2u + Eu acoustic.
  The second-order kernel transforms like [alpha beta] x [mode], so only the even (Raman) modes can carry it; the odd
  (IR) modes must give ~0 numerically. This is a useful internal check.

## 1. Plan
1. relax (internal coordinates, cell fixed) -> scf (12x12x12 k, 90 Ry) [debug partition, minutes].
2. ph.x at Gamma only (ldisp, nq=1x1x1, epsil=.true., tr2_ph=1e-16) + dynmat.x asr=crystal -> frequencies, irreps.
3. bands along the BCT2 path (pw.x bands) for the Wannier check; projwfc not needed if projections are chosen from chemistry.
4. nscf on the 8x8x8 coarse grid (explicit list in [0,1)), nbnd large enough for disentanglement to ~CBM+7 eV.
5. EPW: wannierize (Bi s,p,(d); O s,p; Se s,p(,d)), band_plot along the same path -> RMS/max deviation.
6. EPW kernel runs: nkf = 24^3 (timing), then 36^3, 48^3, 64^3, ... as the 20 node-hour budget allows; converge the peak.
7. Deliverables: kernel/Gamma_alphabeta_s.dat (+ per-mesh copies), RESULT.json, REPORT.md, jobs.log, DONE.

## 2. Running log
- 07:18 LUMI time (04:18 UTC): job 22926410 (debug, 128 cores, 58 s): pw.x relax at the sealed cell, 12x12x12 k, 90 Ry.
  Result: already converged at the given positions (0 BFGS steps, |F| = 5e-5 Ry/bohr, P = 0.24 kbar). Decision: use the
  sealed positions unchanged (they are the equilibrium of this PBE/PseudoDojo setup). conv_thr 1e-10 Davidson ran fine.
- Queue check: `small` predicted start ~5 h away (511 pending), `standard` ~2 days. `debug` idle. Strategy: short
  (<10 min) debug jobs one at a time for the cheap steps; small/standard only for the long kernel runs.
- 07:22 job 22926459 (debug, 3 min 53 s): scf (conv_thr 1e-12, 163 irreducible k) + bands along the BCT2 path
  G-X-Y-S-G-Z-S1-N-P-Y1-Z (201 explicit points) with nbnd = 80. VBM = 10.674 eV (on S-G), CBM = 10.998 eV (G),
  indirect PBE gap 0.324 eV, smallest direct gap 1.25 eV. Band ranges (rel. VBM): Se 3d -46 (5 bands), Bi 5d -23
  (10 bands), O 2s -19..-17 (2), Bi 6s + Se 4s -12.7..-7.8 (3), O 2p + Se 4p -5.9..0 (9), Bi 6p +0.32..+6.0 (6),
  then bands 36-37 at 5.7..10.1 eV, band 38+ above 9.6 eV.
- 07:27 job 22926460 (debug, 54 s): nscf on the explicit 8x8x8 grid (512 k in [0,1)), nbnd 80, nosym/noinv,
  diago_thr_init 5e-6 (toolchain quirk).
- Phonons: the small-partition job 22926461 (dependency chain) is predicted to start 12:40, so I also run ph.x in debug in
  <10-min chunks (max_seconds = 540 + recover): job 22926510 (chunk A). Chunk B submitted after the Wannier test
  (debug allows 2 queued jobs per user).
- Wannier design (job 22926511, two variants, wannierize-only, hr written for an offline interpolation check):
  V1: 20 WFs Bi s,p / O s,p / Se s,p, frozen up to VBM+5.5 eV (below band 36), dis window to VBM+8.
  V2: 30 WFs Bi s,p,d / O s,p / Se s,p, frozen up to VBM+9.0 eV (below band 38), dis window to +17 eV.
  Both exclude bands 1-15 (Se 3d, Bi 5d).
- 07:40 ph chunk A (22926510): epsil + irreps 1-3 in 9 min (tr2_ph 1e-16 is slow; ~2-3 min per irrep on 128 cores).
  Chunk B (22926656, 9 min): irreps 4-8. Chunk C (22926960) running for irreps 9-10 + dynmat + collection.
- 07:47 Wannier test (22926655): V1 converged (wannier90 128 s; Omega_I 23.5, total spread 31.4 A^2, Bi p spreads 2.8 A^2).
  Offline interpolation from bos_hr.dat vs DFT on the 201-point path (first test, not the final EPW check):
  bands 16-29 (valence): max 0.5-3.4 meV; bands 30-33: max 12, 1.9, 4.2, 18.7 meV; bands 34-35: 220/137 meV
  (at Z, where bands 35 and 36 are degenerate at VBM+5.87 eV, i.e. the frozen window top cuts through a crossing).
  V2 (30 WFs with Bi d): disentanglement crawled (1484 iterations, Omega_I 58.8, Delta 1e-7) -> killed at the 11-min limit.
  Next test (22926961): V2b = V2 with dis_conv_tol 1e-9 / 800 iterations; V6 = SCDM (erfc, mu = VBM+8, sigma 2 eV), 30 WFs.
  Both 30-WF variants again exceeded 9 min in wannier90 (serial library call, 512 k x 65 bands) -> abandoned; the kernel cost
  also scales as nbnd^3, so the 20-WF model is the practical choice. Testing V1b (frozen to VBM+5.0, dis window to +10).
- 08:22 DFPT at Gamma complete (3 debug chunks, 26 min total on 128 cores). ph.x mode symmetry (D4h) and dynmat.x with
  asr='crystal' (||dyn(ASR)-dyn|| = 5e-4): acoustic 0,0,0 (raw -3.4/-3.1 cm-1); Eu 14.67 cm-1 (0.440 THz, IR 18.4);
  A2u 43.15 (1.294 THz); Eg 61.65 (1.848 THz, R); A1g 155.59 (4.665 THz, R); Eu 251.36 (7.536 THz); B1g 339.57
  (10.180 THz, R); A2u 364.09 (10.915 THz); Eg 414.97 (12.441 THz, R). eps_inf = 14.58 (xx) / 10.72 (zz);
  Z*(Bi) = 6.23/5.47, Z*(Se) = -4.43/-3.18. A1g 155.6 cm-1 agrees with the Raman literature (~159 cm-1).
  The ldisp run puts dvscf/patterns in tmp/_ph0 (not ./_ph0): collected by hand into run/save/.
  Fallback small-partition phonon job 22926461 cancelled (never started, 0 nh).
- 08:50 V1b test (22927182, 4 min): valence max 1.4 meV, bands 30-33: 3.1/2.2/5.1/10.6 meV; window up to VBM+5.0 eV:
  RMS 1.6 meV, max 75 meV (band 34/35 near the window top); conduction window [0.23, 5.03] eV: RMS 3.2 meV.
  Adopted V1b (20 WFs: Bi s,p; O s,p; Se s,p; frozen [-9.5, 15.7] eV abs = up to VBM+5.0; dis window to 20.7 eV).
- 09:02 EPW main run (22927235, 15 min): Wannierization went to 2000 iterations: the symmetric solution (Omega 30.98 A^2,
  reached in the test) is a saddle; the main run left it at iteration ~300 and converged to Omega = 27.69 A^2 with slightly
  hybridized (off-centre) Bi WFs. Omega_I identical (same disentangled subspace). I keep this lower-spread gauge (bos.ukk).
  The e-ph step then aborted: EPW wants dvscf_dir/bos.phsave/patterns.1.xml (directory), not bos.patterns.1.xml. Fixed by
  copying tmp/_ph0/bos.phsave into run/save. Rerun as epw_main2 with wannierize = .false. (reuses bos.ukk).
- 09:10 epw_main2 (22927337, 5.5 min): coarse e-ph at q=Gamma on 8x8x8 k, Wannier transform (927 WS vectors for
  electrons), velocity matrix elements, epmatwp (1.3 GB) + *.fmt written; band_plot on the 201-point path.
  EPW band.eig vs DFT: valence RMS 0.32 meV / max 1.13 meV; conduction [0.23, 5.03] eV above VBM RMS 3.1 meV / max 73 meV
  (band 34 at the frozen-window top at Z); up to +6.03 eV RMS 24 meV / max 232 meV (bands 34-35 above the frozen window,
  where DFT band 36 crosses). EPW phonons at Gamma (meV): 0,0,0 | 1.901x2 Eu | 5.413 A2u | 7.662x2 Eg | 19.291 A1g |
  31.164x2 Eu | 42.094 B1g | 45.148 A2u | 51.433x2 Eg  (= dynmat ASR values within 0.1 cm-1).
- Kernel runs: epwread from epw/*.fmt + run/tmp_nscf/bos.epmatwp; lindabs, omega 0.01..6.00 step 0.01 eV, degaussw 0.025,
  fsthick 8 eV around Ef = 10.836 eV (mid-gap), eps_acoustic 10 cm-1, full fine mesh (mp_mesh_k false), nqf 1x1x1.
  Timing run kern12 (12^3 = 1728 k) submitted to debug to measure the per-k cost before choosing the production meshes.
- 09:16 kern12 (22927517, 53 s): ep-interp 28 s for 1728 k on 128 pools -> ~2.1 s per k-point per rank. Projections:
  24^3 4 min, 36^3 12 min, 48^3 29 min (0.5 nh), 64^3 68 min (1.1 nh), 96^3 3.8 h. nbndfst = 16 (Wannier bands 5-20,
  2.85-16.7 eV abs) inside fsthick. Memory: each rank keeps the full epmatwp (1.33 GB) -> 171 GB per 128-rank node,
  plus ~0.1 MB per fine k per rank -> 96^3 needs 2 nodes (or 64 ranks/node).
  12^3 kernel sanity: even (Raman) modes dominate: B1g (42.09 meV) xx=yy ~37 A^2/eV peak at 2.33 eV, A1g (19.29 meV)
  xx=yy ~28 at 1.80 eV (zz tiny), Eg modes in xz/zx; odd modes are 1-3% of the leading ones (not exactly 0 because the
  adopted Wannier gauge is slightly off-centre; a symmetry diagnostic I track with the mesh).
- 09:18 queue: small predicted start 16:11, standard 2026-10-18 21:09. Submitted kern24 (debug, 22927524) and
  kern36/48/64 on small (22927535/22927536/22927537) to let them backfill.
- 09:22 kern24 (22927524, 4 min, ep-interp 206 s as projected). B1g peak 46.3 A^2/eV at 2.55 eV (12^3: 74 at 2.33),
  A1g peak 40.9 at 3.80 eV (12^3: 56 at 1.80) -> far from converged at 24^3, as expected for a 25 meV Gaussian in 3D.
  Odd-mode residuals halved (Eu 0.8 vs 2.0) -> they are spurious mesh/gauge noise and vanish with refinement.
  Memory (sacct MaxRSS per rank): 190 MB at 12^3, 206 MB at 24^3 -> epmatwp is distributed, ~0.17 MB per fine k per
  rank: 96^3 fits on one node (~1.2 GB/rank); 128^3 would need 2 nodes. Submitted kern96 (small, 1 node, 22927568).
  Prepared kern128 (2 nodes, 256 pools, ~9 nh) in case 64^3 -> 96^3 is not yet converged.
- 11:25 small queue still holds kern36/48/64/96 (521 pending jobs; a fresh --test-only now predicts 2026-10-18 02:42).
  To keep the convergence series moving I run 32^3 (32768 k, ~9 min, inside the <10-min debug guidance) on debug.
- 11:34 kern32 (22929355, 8.6 min). Peaks (I_sum): B1g 46.1 at 2.46 eV (24^3: 46.3 at 2.55), A1g 41.6 at 3.81 (40.9 at
  3.80), Eg(7.7 meV) 15.3 at 2.90, Eg(51 meV) 11.4 at 4.16; odd residual 0.74. The spectra are still spiky (point-to-point
  jumps of 30-50% at 0.04 eV spacing) -> the peak maximum is noise-dominated below ~64^3. Submitted kern128 (2 nodes,
  256 pools, ~9 nh, 22929517) on small as well; it will be cancelled if 64^3 -> 96^3 is already converged.
- 13:24 kern36/48/64/96/128 all started on small at once. kern96 and kern128 died OOM within a minute: the small
  partition gives 896 MB per core by default (112 GB per node) and the per-rank footprint is ~195 MB + 0.12 MB per fine
  k-point (sstat: 237/292/440 MB per rank at 36^3/48^3/64^3) -> 96^3 needs ~1 GB per rank. Resubmitted both with
  --mem=200G (22931791: 96^3 on 1 node; 22931793: 128^3 on 2 nodes); predicted start 2026-10-18 05:00.
- 13:36 kern36 (11.7 min): B1g max 38.4 at 2.44 eV, A1g 39.9 at 3.81 eV, Eg(7.7) 15.1 at 2.90, Eg(51) 12.8 at 4.16;
  odd residual 0.69. B1g and A1g peak heights are within noise of each other (~40 A^2/eV) -> which mode is "largest"
  must be decided by the fine meshes.
- 14:28 kern48 (27.5 min, 0.46 nh) and kern64 (63.7 min, 1.06 nh) done. Peaks (I_sum, A^2/eV):
  A1g 42.0 at 3.79 (48^3), 40.4 at 3.80 (64^3); B1g 35.9 at 2.39, 34.9 at 2.37 (the B1g coarse-mesh values of 46 were
  spikes); Eg(7.7 meV) 15.4/15.7 at 2.91/2.90; Eg(51 meV) 12.3/12.2 at 4.16/4.15; odd residual 0.64/0.63.
  Global peak: A1g at 3.80 eV from 36^3 on; height fluctuates 39.9/42.0/40.4 (+-3%) -> wait for 96^3/128^3.
  Symmetry of the 64^3 tensor: A1g xx = yy (14.07+10.54i), zz = 4.02+3.26i, off-diagonal ~1e-3; B1g xx = -yy, zz = 0;
  Eg only xz/zx/yz/zy. Provisional deliverables written with the 64^3 kernel (RESULT.json, kernel/Gamma_alphabeta_s.dat).
- 16:40 (LUMI time) LUMI entered a maintenance break (ssh refused: "Maintenance break ongoing"). kern96 (22931791) and
  kern128 (22931793) were pending; polling every 10 min until the system is back.
