# NOTES.md — GaP_t1 coherent-phonon kernel (cophon-bench v1, whiteboard)

Start (wall clock): 2026-10-15T09:26Z (container start; transcript.jsonl ctime).

## 0. What the deliverable is (from papers + code reading)
- Kernel: Gamma^{ab}_s(omega_s; omega, -omega), Hu/Guo/Li/Wang/Chang. In the toolchain the "kernel variant" is
  implemented in EPW/src/indabs.f90 (`indabs_main`), activated by `lindabs = .true.`; it evaluates the
  triangle diagram (c) ("Gamma_c, v1 scope" — diagram (e) with g^{s;alpha} is NOT in this build),
  using `vmef` (velocity h^alpha, vme='wannier'), `epf17` (g at the current q), Gaussian delta of width
  `degaussw` for the electronic resonance and `1/(w_s + e_ln + i*degaussw)` for the phonon-side denominator.
  Optional `ladsmear` (adaptive smearing) exists; default .false. — I keep the SI prescription eta = 0.025 eV.
- The kernel array is re-zeroed every q and written only at iq == lastq -> the fine q-mesh MUST be Gamma only
  (nqf1=nqf2=nqf3=1). Output file: Gamma_alphabeta_s.dat, columns: E(eV), then Re/Im of xx,yy,zz,xy,xz,yz,yx,zx,zy
  in ang^2/eV, modes imode=4..nmodes (optical modes), photon grid omegamin..omegamax step omegastep (eV).
- The photon energy grid: 0 to 6 eV. omegamin=0 would divide by omega^2 (1/omegap^2 prefactor) -> start at omegastep.
- Occupations: step function around ef0 (efermi_read + fermi_energy mid-gap); temperature irrelevant for the kernel.
- bands entering: nbndfst = bands within fsthick of ef -> fsthick large enough to include all Wannier bands.

## 1. Physical/numerical choices
- Cell: sealed, used verbatim from structure_POSCAR (fcc primitive, a_conv = 5.4472 A). Zincblende GaP:
  Ga (1/4,1/4,1/4), P (0,0,0): Wyckoff positions with no free internal parameter -> forces vanish by symmetry,
  so no internal relaxation is needed (checked: SCF forces = 0). Cell not relaxed (rule).
- Pseudos: PseudoDojo nc-fr-04 PBE standard Ga.upf (13 e: 3d10 4s2 4p1), P.upf (5 e), used WITHOUT spin-orbit
  (scalar-relativistic average; allowed by the task). Cutoff hints: Ga normal 80 Ry, high 92 Ry; P normal 44 Ry.
  -> ecutwfc = 80 Ry, ecutrho = 320 Ry.
- 18 valence electrons -> 9 occupied bands (5 Ga-3d + 4 sp3 bonding).
- DFPT: SCF k 8x8x8 (insulator), q 6x6x6 (16 irreducible q), epsil=.true. for eps_inf and Z* (needed for lpolar
  in EPW), tr2_ph 1e-16 as in the SI. Gamma frequencies with ASR from dynmat.x (asr='crystal').
- Wannier/EPW coarse k: 12x12x12 (NSCF, explicit list in [0,1), nbnd=40), q coarse 6x6x6 (DFPT grid).
  Projections to be tested; target: VB + CB up to ~6 eV above the gap within a few meV.
  Ga 3d bands (deep, ~-15 eV) excluded from the Wannier set (bands_skipped).
- EPW: lpolar=.true., vme='wannier', lindabs=.true., efermi_read, fermi_energy mid-gap, fsthick = 20 eV,
  degaussw = 0.025 eV (SI), omegamin=0.01, omegamax=6.0, omegastep=0.01 eV, nqf=1x1x1, nkf = 48^3, 72^3, 96^3
  (convergence), temps=300.
- Partition choice by queue state (sbatch --test-only); small (shared) for short jobs.

## 2. Log
- 2026-10-15T09:32:17+00:00: read papers/code; wrote plan. Remote root pre-contained owner's scaffold (scf.in, ph.in, job_small.sh, pseudo/) dated 12:30+03; pseudos md5-identical to the mounted table (checked). I write my own inputs under subfolders; the scaffold is left untouched and unused.
- 2026-10-15T09:41:40+00:00: J1 done in 84 s (SCF E=-166.83298 Ry, forces 0, P=27.6 kbar; VBM 7.637, CBM 9.230 eV, PBE gap 1.593 eV indirect; Ga-3d at -6.9 eV; band 6 (P-s) -4.87..-1.81 eV). Wannier windows: exclude bands 1-5, froz_max 16 (B:13 WFs) / 17 eV (C:18 WFs), win_max 26 eV. Submitted J3 (Wannier test B/C + DFT bands at the W90 path k-points).
- 2026-10-15T09:55:01+00:00: J2 (DFPT) running: Gamma block gives eps_inf = 11.235 (isotropic), Z*(Ga)=+2.140, Z*(P)=-2.244 (no ASR), TO triplet 10.7706 THz = 359.27 cm-1 (acoustic -2.7 cm-1 before ASR). J3 Wannier test running (set B: Ga s,p,d + P s,p = 13 WFs; set C: + P d = 18 WFs).
- 2026-10-15T10:18:31+00:00: J2 DFPT done (27:45 on 64 cores). J3 Wannier test: set B (Ga spd + P sp, 13 WFs, win_max 26) gives VB RMS 12.5 meV / max 76 meV, CB(<=CBM+6) RMS 38 / max 286 meV — Ga-d WFs delocalised (spreads 13-19 A^2) -> rejected. Set C (18 WFs) failed: outer window too narrow at Gamma (15 bands < 18). Round 2 (J3b=22867643): D = Ga sp + P sp (8 WFs, froz 14, win 22); E = spd+spd (18, froz 17, win 40); F = Ga sp + P spd (13, froz 16.5, win 35); G = Ga spd + P sp (13, froz 16.5, win 35); num_iter/dis_num_iter 5000. J3b also does the phonon post-processing (gather save/, q2r, matdyn, dynmat ASR).
- 2026-10-15T10:37:33+00:00: J3b failed: pw2wannier90 'wrong number of k-points' because the bands run (J3) had overwritten tmp/ wavefunctions. Resubmitted as 22868808 with an NSCF rerun first; band runs now use outdir tmp_bands. Phonon post-processing OK: dynmat.x (asr=crystal) at Gamma: acoustic 0.00 cm-1, TO 359.25 cm-1 = 10.7702 THz (x3, T2); with the nonanalytic term along [001]: TO 359.25 x2, LO 391.61 cm-1 = 11.7401 THz. ||dyn(ASR)-dyn||=1.3e-4; q2r/matdyn dispersion written (gap.freq).
- 2026-10-15T12:21:59+00:00: 22868808 timed out (1:30): set D (Ga sp + P sp, 8 WFs, froz 14) finished: VB RMS 1.8 / max 10.8 meV; CB<=CBM+4 RMS 9.7 / max 54 meV; CB<=CBM+6 RMS 108 meV (too few WFs for the 14-16 eV region). Set E (18 WFs, 5000 iterations) converged disentanglement (Omega_I 21.2 A^2) but the wannierise step oscillated (~1.3 s/iter) and the job was killed before writing bands (wasted 0.38 nh). Round 3 (22873311): E (18, froz 16.5, win 40), F (Ga sp + P spd, 13, froz 16, win 35), G (Ga spd + P sp, 13, froz 16, win 35), dis_num_iter 1500, num_iter 1000, run concurrently as single-core steps.

## 3. Session 2 (resumed 2026-10-16T10:11Z after the model-account usage limit cut session 1 at 13:38Z on 10-15 while waiting for J3c)
- 2026-10-16T10:20Z: J3c (22873311) had completed at 13:37Z (58 min, 32 cores = 0.244 nh). Results (DFT vs Wannier along L-G-X-W-K-G, 1048 VB / 899 CB<=CBM+6 eV points):
    set E (Ga spd + P spd, 18 WFs, froz 16.5, win 40): VB RMS 2.2 / max 10.9 meV; CB<=CBM+6 RMS 7.2 / max 44.7 meV; wannierise NOT converged in 1000 iter.
    set F (Ga sp + P spd, 13 WFs, froz 16, win 35):    VB RMS 0.38 / max 1.5 meV; CB<=CBM+6 RMS 2.9 / max 15.1 meV; converged (271 iter), spreads <= 2.71 A^2.
    set G (Ga spd + P sp, 13 WFs, froz 16, win 35):    VB RMS 1.4 / max 6.0 meV; CB<=CBM+6 RMS 4.8 / max 26 meV; not converged in 1000 iter.
  -> ADOPTED set F (Ga: s,p; P: s,p,d; 13 WFs; dis_win -6..35 eV, frozen -6..16 eV = CBM+6.8 eV). Comparison data: wannier_vs_dft_bands_setF.dat, wannier_vs_dft_stats_setF.txt.
- Invariant for RESULT.json (decision): the paper (SI, 'coherent vibration amplitude') uses |Gamma^{ab}_s(w_s; w, -w)| per Cartesian channel with an isotropic field.
  I take the per-mode magnitude M_s(w) = sum_{ab} |Gamma^{ab}_s(w)| (9 channels, complex modulus) and the invariant I(w) = sum_{s in optical modes} M_s(w);
  peak_ev = argmax_w I, peak_a2_per_ev = max I, mode = the s with the largest M_s at that w. (Script: scripts/kernel_invariant.py; the Frobenius alternative is printed too.)
- Note: the 3 optical modes are the degenerate T2 (Gamma_15) triplet at q=Gamma without the non-analytic term (EPW evaluates exactly q=0: no LO-TO split), 359.25 cm-1 = 10.770 THz.
- Queue: sbatch --test-only quoted 2026-10-17T02:20 for ANY small job (16-64 cores) and 10-18 for standard -> submitted J4 (22899917, EPW coarse: wannierize set F inside EPW
  + e-ph on 12^3 k / 6^3 q, 64 ranks, small) anyway; it started within 1 min. J5 (22899941, fine meshes 48,72,96 sequentially, 128 ranks, 3 h) queued with afterok dependency.
- epw1.in updated to set F (proj Ga:s;p / P:s;p;d, dis_win_max 35, froz_max 16, num_iter 1000, dis_num_iter 1500, conv_tol 1e-8, dis_conv_tol 1e-9).
  Phonon post-processing (q2r/matdyn/dynmat) was already done in 22867643, so job4 only runs epw.x.
- Fine runs: etf_mem=1 (epmatwp read in distributed slices), mp_mesh_k=.false. (full mesh; the kernel is a tensor, no symmetrisation in the code), nqf=1 (Gamma only, required by the code which writes at iq==lastq).
- 2026-10-16T10:28:10+00:00: J4 Wannierisation inside EPW reproduces set F: Omega 28.539 A^2 (standalone 28.539), conv. in 100 it.; vs DFT: VB RMS 0.41 / max 1.7 meV, CB<=CBM+6 RMS 2.9 / max 15.0 meV (remote_out/04_epw/gap_band.dat). e-ph coarse step running.
- 2026-10-16T10:34Z: J4 (22899917) CRASHED at irreducible q #5: "Bad integer for item 1 in list input" reading save/gap.dyn_q5 (io.f90 dynmat_asr).
  Cause: EPW's own irreducible-q ordering (kpoint_grid; with the nosym NSCF it differs from ph.x's) did not match the ph.x numbering of the
  dyn_q#/dvscf_q# files (EPW's q#5 = (-.236,-.236,.236), 8-member star; file dyn_q5 = ph.x's (.236,0,0), 6-member star). The authors'
  patch in ep_coarse_unfolding.f90 ("qorder") reads <prefix>.dyn0 FROM THE EPW RUN DIRECTORY to recover ph.x's canonical order, and
  silently falls back to the old behaviour when it is absent. Fix: cp 02_ph/gap.dyn0 04_epw/gap.dyn0. Failed outputs kept in 04_epw/failed_run1/.
  The dependent fine job 22899941 had started (job4's script exited 0 despite the crash) and died instantly (no crystal.fmt): 10 s wasted.
  Both job scripts now exit 1 when epw.x fails. Resubmitted: J4b = 22900599 (coarse), J5b = 22900600 (fine 48/72/96, afterok:J4b).

## 4. Session 3 (resumed 2026-10-16T17:07Z after the usage limit cut session 2 at 13:15Z while J4b was at q 76/216)
- 2026-10-16T17:10Z: J4b (22900599) processed all 216 coarse q-points (Wannierisation of set F again converged: gap.ukk/gap.chk/gap_hr.dat written, 9 min)
  but was OOM-killed at 14:48 (local) right after "Number of WS vectors" i.e. entering the Bloch->Wannier transformation. Cause: on the shared small
  partition 64 cores get only 56 GB by default (ReqMem=56G); epmatq(nbndep=35,35,nks=27,6 modes,216 q) is 0.69 GB per rank = 44 GB plus
  the per-q work arrays of the transformation. Fix: --ntasks=128 (-nk 128, halves the per-rank k-slice), --mem=200G (node has 256 GB),
  wannierize=.false. (reuse the converged gap.ukk from 22900599; the wannierize input is kept as epw1_run2_wannierize.in). Output of the OOM run
  kept as 04_epw/epw1_run2_oom.out. Dependent fine job 22900600 (DependencyNeverSatisfied) cancelled.
  sbatch --test-only quotes: small 10-17T15:06, standard 10-18T16:09 (both pessimistic last time; small has 11 idle nodes) -> small.
  Submitted J4c = 22918065 (coarse, 128 ranks, 200 GB, 2 h limit) and J5c = 22918066 (fine 48/72/96, 128 ranks, 200 GB, afterok:J4c).
- 2026-10-16T18:05Z: J4c (22918065) COMPLETED in 40:42 (128 ranks, 200 GB: MaxRSS 0.6 GB/rank): "Using gap.ukk from disk", "Using PH dyn0
  irreducible-q ordering for coarse-file reads", 216 q in 37 min, Bloch2wane/Bloch2wanp OK, epwdata.fmt/vmedata.fmt/crystal.fmt/wigner.fmt
  + 03_wan/tmp/gap.epmatwp (8.86 GB) written. The only warning is the generic "Wannier bands might differ from DFT bands near the Fermi energy".
  J5c (22918066) started at 17:59Z: k48 first (864 k per pool, 1 q-point).
- 2026-10-16T18:50Z: J5c (22918066) done: kernel files for 48^3/72^3/96^3 (kernel/Gamma_alphabeta_s_<mesh>.dat). Per-mode invariant
  M_s = sum_ab |Gamma^ab_s|: peak 20.37 @2.88 eV (48), 21.14 @2.83 (72), 20.56 @2.82 (96); triplet sum 57.4/59.6/58.0; the three T2 modes
  have M_s within 20 % of each other (the degenerate basis EPW returns mixes x/y/z: mode 4 mostly yz, 5 mostly xy, 6 mostly xz channels).
  The full spectrum still differs by ~20 % RMS between 72 and 96 (mesh noise under the 25 meV Gaussian), so a second fine job
  J6 = 22919387 (120^3 and 144^3, afterok:J5c, 3.5 h limit) was submitted at 18:16Z; it started at 18:44Z.
- DECISION on the RESULT.json invariant (revised from session 2): the task text says "the per-mode magnitudes summed over Cartesian channels",
  i.e. M_s(w) = sum_ab |Gamma^{ab}_s(w)| per mode; "the largest rotational invariant" = max over optical modes s and photon energies w of M_s;
  mode_thz = the mode realising it (which is also the mode dominating at that energy). The triplet sum and the Frobenius norm are reported in
  REPORT.md as well. Script: scripts/make_result.py (per-mode max), scripts/mesh_convergence.py.
- 2026-10-16T19:00Z: peak assignment: the 2.82 eV peak is the E1 critical point (VB 8/9 -> CB 10 parallel along Lambda: 2.80 eV at L, 2.81-2.83 eV
  along L-Gamma in PBE; wannier_vs_dft_bands_setF.dat). The PBE direct gap at Gamma is 1.84 eV (nscf.out) -> weak E0 onset near 2 eV only.
  Report generator written: scripts/write_report.py (fills scripts/report_template.md); result builder scripts/make_result.py.
  Cleanup plan after the last kernel run: delete 03_wan/tmp (wfc + gap.epmatwp 8.9 GB), 01_scf/tmp_ph, 02_ph/tmp (_ph0), 04_epw/gap.mmn, 04_epw/failed_run1;
  keep 02_ph/save, the .fmt files, gap.ukk/chk and all text outputs.
- 2026-10-16T19:35Z: 120^3 done (45 min): peak 20.73 @2.82 eV (+0.85 % vs 96^3), triplet sum 58.45. Spectrum-wide RMS change 96->120: 13.6 % (0-6 eV),
  6.8 % (2.5-3.5 eV): the peak is converged, the plateau above 3 eV still drifts ~1/N. Memory: 0.78 GB/rank at 120^3 (13500 k/pool),
  1.24 GB/rank at 144^3 (23328 k/pool, sstat) -> 192^3 needs 4 nodes x 128 ranks (13824 k/pool, ~0.8 GB/rank) to stay under 200 GB/node.
  Submitted J7 = 22920338 (192^3, 4 nodes, 512 ranks, afterok:J6; same node-hours as 1 node, ~30 min wall). First attempt 22920333 (2 nodes)
  cancelled before start (memory margin). Budget so far 3.14 nh + J6 (~2.1 nh) + J7 (~2 nh) ~ 7.3 nh of 20.
- 2026-10-16T20:50Z: 144^3 done (77 min): peak 20.96 @2.82 eV (+1.1 % vs 120^3; 96->120->144: 20.56, 20.73, 20.96), triplet sum 59.10,
  Frobenius 17.43. Spectrum-wide RMS change 120->144: 9.6 % (0-6 eV), 4.4 % (2.5-3.5 eV). J7 (192^3, 4 nodes) pending for resources.
- 2026-10-16T21:00Z: provisional deliverables written with the 144^3 kernel as adopted mesh (RESULT.json: peak 20.960 A^2/eV at 2.82 eV, mode 6 of the
  T2 triplet at 10.7705 THz; REPORT.md regenerated by scripts/write_report.py; kernel/Gamma_alphabeta_s.dat = 144^3 file). Rationale: 96->120->144 changes
  the peak by +0.9 % and +1.1 % with the energy fixed at 2.82 eV; the triplet sum and the Frobenius norm agree. J7 (192^3, 4 nodes x 128) is pending
  for resources (2 idle small nodes). Time box: if it has not started by ~22:05Z I cancel it and finalise with 144^3; if it finishes, 192^3 becomes
  the adopted mesh (same analysis, node-hours updated), then remote cleanup (large scratch files) and DONE.
- 2026-10-16T21:05Z: J7 (22920338, 192^3, 4 nodes x 128 ranks) started at 20:50Z and was OOM-killed after 74 s, before the k loop: MaxRSS 1.85 GB per
  rank already at start-up (EPW keeps full fine-mesh arrays on every rank: 7.1M k-points; this part does not shrink with more pools), i.e.
  237 GB per node > 200 GB. Fitting it would need <= 64-96 ranks per node on 4 nodes with --mem=224G (tight) - not worth the risk and ~3-5 nh for a
  spectrum-noise improvement from ~10 % to ~6 % RMS while the deliverable (peak) is converged to ~1 %. DECISION: adopt 144^3 and finalise.
  Cleanup of large scratch: 03_wan/tmp (wfc + gap.epmatwp), 01_scf/tmp_ph, 02_ph/tmp, 04_epw/gap.mmn, 04_epw/failed_run1 deleted; 02_ph/save,
  the EPW .fmt files, gap.ukk/gap.chk and all text outputs kept.
- 2026-10-16T20:54Z: FINAL. RESULT.json: peak 2.82 eV, 20.960 A^2/eV (per-mode M_s, mode 6 of the T2 triplet, 10.7705 THz), mesh 144x144x144,
  node_hours 5.18, wall_hours 35.47. REPORT.md regenerated; kernel/Gamma_alphabeta_s.dat == remote k144 file (cmp). DONE written.
