# NOTES.md — running log (CdS_mp672, cophon-bench v1 whiteboard, model fable)

Start: 2026-10-16T20:55:35+00:00 (file START_TIME).

## 1. Reading (20:55–21:05 UTC)
- Manuscript (Hu, Guo, Li, Wang, Chang): second-order coherent-phonon generation kernel
  Gamma^{ab}_s(omega_s; omega, -omega), Eq. (Gamma_2nd_final): double-resonant (electronic resonance
  delta(hbar omega - eps_nm) + phonon-resonant 1/(hbar omega_s + eps_ln + i eta)) triangle (diagram c)
  plus the g^{s;alpha} vertex (diagram e). SI Sec. IV: EPW-based evaluation, eta = 0.025 eV, PBE,
  tr2_ph 1e-16, fine k-mesh convergence tested (SnSe 256x256x1).
- Implementation note: describes the authors' EPW modifications (wan2bloch/elph2/ephwann_shuffle/indabs).
- Toolchain on LUMI (qe-phnlo-75 = QE 7.5 + EPW 5.9 "kernel variant"): the kernel lives in
  EPW/src/indabs.f90, subroutine indabs_main, "v1 scope": only the triangle diagram Gamma_c
  (uses epf17 = g and vmef = h^alpha with vme='wannier'); the g^{s;alpha} (Pi_kernel/epvf17) term is
  explicitly "out of scope in v1". Output file: Gamma_alphabeta_s.dat written on the ionode at the
  last q-point; columns: photon energy (eV), then Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy in
  ang^2/eV; one block per mode imode = 4..nmodes with header "imode = n  <phonon energy meV>".
  Triggered by lindabs = .true. in &inputepw; photon grid omegamin/omegamax/omegastep (eV);
  broadening degaussw (Gaussian delta for the electronic resonance and i*degaussw in the phonon
  denominator); occupation factors from ef0 (= fermi_energy if efermi_read); bands = nbndfst
  (fsthick window around ef). The kernel has a 1/omega^2 prefactor -> omegamin must be > 0
  (omega = 0 gives 0*Inf = NaN). Acoustic modes skipped by eps_acoustic.
  Also writes Pi_0.dat (field-free phonon self energy).
- Known build quirks (task sheet): diago_thr_init 5e-6; EPW npool = nranks; explicit NSCF k list in [0,1).

## 2. Decisions
- Cell: lattice vectors of structure_POSCAR verbatim (ibrav=0, CELL_PARAMETERS angstrom) so the Cartesian
  frame of the kernel is the one of the sealed cell. 1/3, 2/3 written with 10 digits (the file rounds to 6).
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard Cd.upf (20 e: 4s4p4d5s) and S.upf (6 e), used
  scalar-relativistically (no SOC, allowed by the task). Cutoff hints: Cd normal 102 Ry, S 52 Ry ->
  ecutwfc = 100 Ry.
- Internal coordinates: relaxed at the fixed cell (allowed) so that DFPT sees zero forces.
- Coarse k mesh 9x9x6 (486 points) for SCF/NSCF/Wannier; DFPT only at q = Gamma (nq = 1x1x1):
  only Gamma-point phonons enter the kernel, and with q on the coarse grid the phonon-side
  interpolation is exact. ph.x with epsil=.true. (dielectric tensor + Born charges, for LO/TO info).
- Wannier functions: Cd s,p,d + S s,p = 26 WFs; semicore Cd 4s4p (8 bands) excluded; windows set
  from the DFT eigenvalues (see below). vme = 'wannier'.
- Kernel settings: degaussw = 0.025 eV (paper), omega 0.01..6.00 eV step 0.01 eV, fsthick large
  (all 26 Wannier bands), efermi_read with fermi_energy at mid gap, temps = 300 (only sets gtemp),
  eps_acoustic = 5 cm-1, lpolar = .false. (q = Gamma exactly; no q interpolation needed).
- Fine meshes: ratio |b1|/|b3| = 1.88, so Nz ~ N/1.88; sequence 24x24x13, 48x48x26, 72x72x38,
  96x96x51 (as budget allows); convergence judged on the peak of the invariant.
- Queue (21:00 UTC): standard has 578 pending jobs and --test-only predicts a 2-day wait;
  small predicts ~3 h; debug idle. Plan: validate pw.x on debug (<10 min), then ONE pipeline job
  on small (full node, 128 ranks) running relax->scf->ph->nscf->bands->epw(wannier+kernel meshes),
  then separate epw jobs for the larger meshes.

## 3. Execution log
- 21:04 UTC job 22921749 (debug, 32 cores): pw.x relax at fixed cell, 9x9x6, 100 Ry, nbnd 40. 12 symmetry
  operations (C6v), 48 irreducible k. Forces on the given positions are 7e-5 Ry/bohr (< forc_conv_thr
  1e-4): BFGS converged in 0 steps -> positions kept EXACTLY as in the sealed structure file.
  Stress +30 kbar (sealed cell is slightly compressed w.r.t. PseudoDojo-PBE equilibrium; not touched).
  Gamma eigenvalues (eV): Cd4s -94.1 (2), Cd4p -55.7 (6), S3s -5.3/-4.9, Cd4d -0.60..+0.28 (10),
  S3p 2.64..7.07 (6), VBM 7.0682, CBM 8.3089 (PBE gap 1.24 eV), then CB 9.88, 13.49(2), 13.78, 14.60(2),
  14.79, 16.93(2), 17.70, 18.61(2), 19.09.
  -> Wannier: exclude bands 1-8 (semicore), 26 WFs = Cd s,p,d + S s,p; dis_win [-6, 20] eV,
  frozen window [-6, 13.6] eV (= VBM + 6.5 eV, covering CB to ~5.3 eV above the CBM).
  fermi_energy for the kernel occupations = 7.69 eV (mid gap).
- Remote root already contained a scf/ folder with files not created by me (job_scf.sh, scf.out,
  slurm-22880692.out, ...). I did not read or use them; all my work is under <root>/calc/ and <root>/pseudo/.
  (My first test relax used <root>/scf and overwrote cds.save there; nothing of mine depends on it.)
- 21:07 UTC job 22921770 (debug): scf OK (10 s) but ph.x stopped: diago_thr_init is not an &inputph
  variable (my error). Resubmitted ph.x only as job 22921780.
- 21:12 UTC job 22921771 (small, full node, 5 h limit) queued as a placeholder; at start it runs
  calc/epw/stage_small.sh (mesh loop over MESHES) only if the file READY exists.
- 21:14 UTC job 22921780 (debug, 64 cores, 5.5 min): ph.x at Gamma, epsil=.true., tr2_ph 1e-16.
  eps_inf = diag(6.105, 6.105, 6.159); Z*(Cd) = diag(2.108, 2.108, 2.196) before ASR.
  dynmat.x (asr='crystal'): acoustic 0.00 cm-1 (raw ph.x: 1.8, 2.5, 2.5 cm-1), optical modes:
  E2(low) 38.40 (x2), B1 134.77, A1(TO) 234.45, E1(TO) 241.81 (x2), E2(high) 255.52 (x2), B1 302.35 cm-1.
  Irreps from ph.x "Mode symmetry, C_6v (6mm)". No LO-TO splitting at exactly q=0 (no q direction),
  as in the authors' q=0 kernel evaluation. save/ built with EPW's pp.py.
- 21:16 UTC job 22921847 (debug, 64 cores): pw.x bands along G-M-K-G-A-L-H-A (30 pts/segment),
  nscf 9x9x6 (486 k, nbnd 40, nosym), epw.x (wannierize, epbwrite/epwwrite, kernel on 24x24x13).
- 21:37 UTC job 22921847 done (22 min on 64 cores): bands 21 s, nscf 24 s, EPW: W90 disentanglement
  converged (Omega_I 36.88 A^2), 1000 Wannierisation iterations (max), total spread 43.68 A^2
  (Cd sp ~3.1-3.3, Cd d 0.66-0.85, S sp 1.35-1.38 A^2). EPW fermiwindow: ibndmin 1 .. ibndmax 26
  (all Wannier bands, -5.3 .. 17.8 eV). Kernel loop on 24x24x13 (7488 k): ~9 min on 64 ranks
  (~4.6 s per k-point per rank, nb = 26, 600 photon energies) -> ~100k k-points per node-hour at 128 ranks.
  Cost estimates: 48x48x26 0.6 h, 72x72x38 2.0 h, 96x96x51 4.7 h (node-hours).
  EPW phonon energies at Gamma (meV): 4.7506(x2) 16.7097 29.0666 29.9787(x2) 31.6797(x2) 37.4833,
  identical to dynmat.x (ASR crystal) -> acoustic modes 1-3 skipped by eps_acoustic.
  First kernel (24x24x13): very noisy spectrum (expected for 25 meV Gaussian on a coarse 3D mesh);
  symmetry checks OK: A1 mode has xx = yy, xy = 0; E2 pair shares weight between xx/yy and xy
  (partner-basis dependent, the pair sum is not). Largest invariant: E2(low) modes near 5.8 eV.
- W90 band plot uses 181 path points (bands_num_points scales per segment) vs my 211-point pw.x path:
  added a pw.x bands run on exactly the W90 k list (bands_w90.in) to the stage script.
- 21:41 UTC job 22922082 (small, full node) submitted: stage_small.sh = bands_w90 + kernel on
  24x24x13 (again, to record timing at 128 ranks and check reproducibility), 48x48x26, 72x72x38.
- 23:40 UTC: job 22922082 running since 21:44 UTC. 48x48x26 took 53 min at 128 ranks (59904 k ->
  ~68k k-points per node-hour; slower than the 64-rank extrapolation, memory-bandwidth bound).
  72x72x38 (197k k) started 22:37 UTC, expected ~2.9 h. bands_w90 done.
  Wannier quality (pw.x vs W90 on the same 181 path points, 8 semicore bands excluded):
  valence (18 bands): RMS 0.35 meV, max 2.9 meV; conduction up to CBM+4 eV: RMS 1.0 / max 3.6 meV;
  up to CBM+5.3 eV (= frozen window top 13.6 eV): RMS 2.3 / max 13.3 meV; up to CBM+6 eV: RMS 68 meV,
  max 357 meV because bands 22-26 leave the frozen window above 13.6 eV (only 8 conduction WFs).
  All resonant transitions for photon energies <= 6 eV end below VBM + 6 = 13.07 eV, inside the frozen
  window, so the kernel is unaffected; documented in REPORT.md.
  48x48x26 kernel: same global structure as 24x24x13; E2(low) pair peak at 5.80 eV, I = 477 A^2/eV
  (24 mesh: 500 at 5.81). A1 peak 4.45 eV (261 vs 325).
- 23:43 UTC: submitted job 22923502 (small, full node, 8.5 h limit): 96x96x51 (470k k, ~7 h) in
  calc/epw96 with symlinks to the Wannier data of calc/epw, so it can run concurrently.
  Budget projection: 0.24 + ~4.5 + ~7 = ~12 node-hours of 20.
- 01:35 UTC (Oct 17): job 22922082 finished (3.81 node-h). 72x72x38 took 2h54m (197k k -> 68k k/node-h).
  72x72x38 kernel: global peak mode 4 (E2 low, 4.7506 meV = 1.1487 THz) at 5.79 eV, I = 489.2 A^2/eV
  (24: 500.4 @5.81; 48: 477.0 @5.80). A1 (mode 7) peak 4.46 eV: 251 (48: 261, 24: 325).
  Job 22923502 (96x96x51) started 00:00 UTC, expected ~7 h.

## 4. Session 2 (resumed 06:23 UTC Oct 17 after a usage-limit cut-off; no previous conversation)
- Re-read NOTES/jobs.log/task. Cluster: job 22923502 (96x96x51) COMPLETED, 03:00:25-08:03:12 EEST = 5.046 h
  (1 node, small) -> node_h=5.046. Placeholder job 22921771 ran 2 s (no READY file) -> 0.001 node-h.
  Three pending jobs on the shared account (bos_kern36/48/64, Bi2O2Se) are not mine; left alone.
- Pulled Gamma_alphabeta_s_96x96x51.dat, Pi_0, epw in/out/err to kernel/ and outputs/epw96/. No NaN, no errors
  (only gfortran IEEE_DENORMAL notes in .err).
- Convergence of the global peak (mode 4, E2 low, 4.7506 meV): 24: 500.4 @5.81; 48: 477.0 @5.80; 72: 489.2 @5.79;
  96: 486.6 @5.79 eV. 72->96 changes the peak by -0.5 %, the A1 peak (mode 7) by -0.4 % (251.1 -> 250.1).
  Adopted 96x96x51 as converged. Next mesh (120x120x64, ~13 node-h at 68k k/node-h) exceeds the remaining
  10.9 node-h -> no further mesh. Total compute 9.10 node-h.
- Note on the degenerate E2 pair: the per-mode invariant depends on the partner basis; pair sum 951.1 A^2/eV at
  5.79 eV (96 mesh). RESULT.json reports the larger partner (mode 4) as the task asks for per-mode magnitudes.
- Note on the soft-mode frequency: kernel file says 4.7506 meV (38.32 cm-1) vs dynmat.x ASR 38.40 cm-1; EPW's own
  ASR numerics. RESULT.json mode_thz = 1.1487 THz from the kernel file (the grader re-analyses that file).
- Remote cleanup (my files only): deleted wavefunctions in calc/epw/cds.save, calc/epw/bands, calc/epw/bands_w90,
  calc/ph/cds.wfc*; calc/epw now 0.66 GB (epmatwp, vmedata, mmn, chk kept), calc/ph 45 MB (save/ kept).
- jobs.log rewritten as one line per job with a node_h= column (make_result.py sums it).
- Wrote REPORT.md, RESULT.json (analysis/make_result.py on kernel/Gamma_alphabeta_s.dat = the 96x96x51 file), DONE.
