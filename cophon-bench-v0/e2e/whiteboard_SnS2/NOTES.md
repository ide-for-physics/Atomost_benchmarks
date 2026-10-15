# NOTES.md — running log (SnS2 coherent-phonon generation kernel)

Session start: 2026-10-14 (UTC+2 local). Working alone; every decision recorded here, one entry per step.

## 0. What the task needs (read from TASK.md and the papers)
- Quantity: second-order light-induced coherent-phonon generation kernel Gamma^{ab}_s(omega_s; omega, -omega), photon
  energy 0–6 eV, every Gamma-point optical phonon mode s, with the authors' modified EPW ("kernel variant") on LUMI.
- Paper definitions (Manuscript.tex eq. "Gamma_2nd_final"; SI Sec. IV "Methods"): kernel = diagram (c) [Raman-like triangle,
  three-band] + diagram (e) [optically perturbed EPC vertex g^{s;alpha}]. Electronic broadening eta = 0.025 eV ("room
  temperature"), delta(hbar*omega - eps_nm) selects resonant transitions.
- "Rotational invariant" is not spelled out in the tex sources (grep of Manuscript/SI/note for "invariant"/"rotational"
  finds nothing relevant). TASK.md paraphrases it as "the per-mode magnitude summed over the Cartesian channels". The only
  rotation-invariant magnitude of a rank-2 tensor built that way is the Frobenius norm
  |Gamma_s|(omega) = sqrt( sum_{ab} |Gamma^{ab}_s(omega)|^2 ). I adopt that as the primary invariant and ALSO report
  sum_{ab}|Gamma^{ab}_s| and |sum_{ab} Gamma^{ab}_s| (isotropic field, as the SI's amplitude formula uses), so the
  reader can pick either convention; all three are computed from the same output file.

## 1. What the code actually does (read on LUMI, EPW/src of qe-phnlo-75; EPW v5.9 file layout)
- Kernel lives in EPW/src/indabs.f90, subroutine indabs_main, switched on by `lindabs = .true.` (standard phonon-assisted
  absorption flag). Comment in the source: "Coherent-phonon generation kernel (Gamma_c triangle + Pi_0), v1 scope ...
  Gamma_e / Pi_kernel (epvf17) are out of scope in v1". So THIS build computes diagram (c) only (the triangle, with
  stock arrays epf17 = g and vmef = velocity). Diagram (e) is not in this build; I state that in REPORT.md.
- Photon grid: omegamin/omegamax/omegastep (eV), nomega = INT((omegamax-omegamin)/omegastep)+1. The kernel carries a
  1/omega^2 prefactor, so omegamin = 0 would give NaN/Inf at the first point -> I start at omegamin = omegastep.
- Broadening: `degaussw` (eV) is the delta-function (Gaussian, w0gauss ngauss=0) width and the i*eta of the
  1/(omega_s + eps_ln + i eta) denominator; `ladsmear = .true.` would use adaptive smearing instead (default .false.).
  I use degaussw = 0.025 eV like the paper.
- Occupations: f_ij from etf vs ef0 (step function); insulator -> ef0 mid-gap is fine (efnew from EPW, or efermi_read).
- Bands: loops run over nbndfst = bands inside the fsthick window around the Fermi level (standard EPW fermiwindow
  selection on the coarse grid). fsthick must therefore be larger than the band window I want (valence + conduction up to
  ~6 eV above the gap): fsthick = 10 eV keeps every Wannier band.
- Output: `Gamma_alphabeta_s.dat` — header, then per optical mode (imode = 4..nmodes, phonon energy meV) a block of
  nomega lines: photon energy (eV), Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy in Angstrom^2/eV. Also `Pi_0.dat`
  (field-free phonon self-energy, diagnostic). Written on the last q-point of the fine q loop; arrays are re-zeroed each
  q-call, so the fine q grid must contain ONLY Gamma (nqf1=nqf2=nqf3=1), which is what the kernel is defined for anyway.
- vmef is the Wannier-interpolated velocity (vme = 'wannier', default in EPW 5.9); units Ry*bohr in the code.
- Modules for the build (prod_build.sh): module load LUMI partition/C PrgEnv-gnu cray-fftw. ldd of epw.x is clean.

## 2. Plan (and why)
1. pw.x SCF, PBE, PseudoDojo nc-fr-04 standard (Sn 14 e: 4d10 5s2 5p2; S 6 e), used scalar-relativistically
   (no SOC; TASK.md allows it; it halves the band count and avoids the degeneracy caveats of the note).
   ecutwfc = 80 Ry (hints: Sn normal 72 / high 84 Ry, S normal 52 / high 64 Ry). k 12x12x6 (c* is ~half of a*).
2. ph.x DFPT at q = Gamma only (epsil = .true. -> eps_inf, Born charges, irreps printed), dynmat.x with ASR for the
   Gamma frequencies. Rationale: the kernel needs g(k, q=Gamma) only. EPW with a 1x1x1 coarse q mesh reproduces the
   coarse Gamma-point g exactly (the q Fourier transform with one R_p vector is the identity), so a DFPT q-mesh would
   buy nothing for this observable and would cost most of the budget.
3. pw.x NSCF on the full 12x12x6 grid (explicit list in [0,1)), nbnd large enough to cover ~10 eV above the gap.
4. wannier90 via EPW (wannierize = .true.) with projections chosen after looking at the DFT bands; frozen window up to
   about CBM + 6 eV; band comparison DFT vs Wannier along Gamma-M-K-Gamma-A-L-H-A from a separate pw.x bands run and
   the Wannier90 band file; RMS/max deviation computed with a script.
5. epw.x kernel runs on fine k meshes 24x24x14, 36x36x21, 48x48x28 (ratio ~ a/c), omegastep 0.02 eV, 0.02-6 eV,
   degaussw 0.025 eV, fsthick 10 eV, temps 300 K, epwread after the first run. Convergence judged on the peak of
   the invariant per mode.
6. Keep budget: everything on `small` (shared) or `debug` for tiny tests; log every job in jobs.log.

## 3. Log of actions
- 22:39 SCF test job 22844786 failed at once: pseudo_dir was given relative to the wrong level. Fixed to the absolute path.
- 22:45 SCF job 22844796 (debug, 32 cores, 19 s): converged in 10 iterations, E = -201.75933377 Ry, PBE band edges
  VBM 5.6009 eV / CBM 7.1723 eV (indirect gap 1.57 eV, consistent with published PBE values ~1.5-1.6 eV for 1T-SnS2),
  pressure 24 kbar and total force 0.015 Ry/bohr (the given cell is not the PBE equilibrium; TASK.md says use the given
  structure, so no relaxation). Davidson ran down to ethr ~ 1e-11 without aborting, so the quirk did not show up here.
- Band analysis of scf.out (scripts/parse_pw_eigs.py): bands 1-5 Sn 4d semicore (-15.3..-15.1 eV), bands 6-7 S 3s
  (-7.9..-5.3), bands 8-13 valence (-1.4..5.6), band 14 Sn 5s-like CB (7.17..8.69), bands 15-18 next CBs (9.4..14.7),
  band 19 starts at 13.58 eV. Number of bands below CBM+6 eV = 13.2 eV: max over k = 18 (13 without the semicore).
  => 12 WFs (S s,p + Sn s,p) cannot freeze the window up to CBM+6 eV. Decision: 17 WFs = Sn s,p,d + S s,p, exclude
  bands 1-5, outer window [-9, 24] eV, frozen window [-9, 13.5] eV (band 19 min 13.58 eV, so at most 13 non-semicore
  bands are frozen anywhere; 17 >= 13 OK). Fermi level for EPW occupations: efermi_read with 6.40 eV (mid-gap).
- 22:52 ph.x at Gamma (job 22844824, small, 32 cores) and NSCF 12x12x6 full grid, nbnd 40 (job 22844840, small,
  64 cores, own copy of the SCF density) submitted; both pending in the busy small queue.
- EPW first run prepared (run/04_epw/epw1.in): wannierize + epbwrite/epwwrite + kernel on fine 24x24x12, omega
  0.02..6.00 eV step 0.02 (300 points), degaussw 0.025 eV, fsthick 12 eV, lpolar false, use_ws true, vme wannier,
  coarse q 1x1x1 and fine q 1x1x1. Fine meshes planned: 24x24x12, 36x36x18, 48x48x24, 60x60x30 (|b3|/|b1| = 0.51).
- 22:56 DFPT at Gamma done (job 22844824, 2 m 41 s wall on 32 cores). ph.x finds point group D_3d (-3m), 12 symmetry
  operations. Frequencies before ASR: acoustic 4.8/6.2/6.2 cm-1 (small residual), optical: E_g 203.31 cm-1, E_u 208.01,
  A_1g 306.94, A_2u 340.49. dynmat.x with asr='crystal' (run/02_ph/dynmat.out): acoustic 0.00, E_g 203.31 cm-1 = 6.0950 THz
  (Raman), E_u 208.08 cm-1 = 6.2381 THz (IR), A_1g 306.94 cm-1 = 9.2019 THz (Raman), A_2u 340.55 cm-1 = 10.2094 THz (IR).
  Experimental Raman for 1T-SnS2: E_g ~205 cm-1, A_1g ~314 cm-1 -> consistent. eps_inf = 7.87 (xx,yy), 4.68 (zz);
  Z*(Sn) = 4.92 (xx,yy), 1.50 (zz); Z*(S) = -2.46, -0.75 (ASR applied by ph.x).
  Files for EPW staged as run/01_scf/save/{sns2.dyn_q1, sns2.dvscf_q1, sns2.phsave/} (pp.py convention).
- 22:54 NSCF job 22844840 finished in 37 s but produced 1320 k-points instead of 864: pw.x treats an explicit list in an
  'nscf' run as irreducible points of the full lattice group (D_6h, 24 ops) and generates the images needed for the lower
  crystal group (D_3d, 12 ops). EPW needs exactly the nk1*nk2*nk3 full grid. Fix: nosym = .true., noinv = .true. in the
  NSCF (and in the later 'bands' run). The already-submitted EPW job 22845108 was cancelled before it started (0 cost).
- 23:05 NSCF rerun (job 22845135) submitted, EPW first run (job 22845136) chained with --dependency=afterok.
- 23:46 EPW run 1 (job 22845136, 32 tasks, 29 m 43 s) finished. Wannier90 (sns2.wout): 17 WFs, Omega_I 29.76,
  Omega_D 0.26, Omega_OD 7.61, total 37.64 Ang^2 (spreads 1.5-3.7 Ang^2 each). The disentanglement stopped at the
  3000-iteration cap with Omega_I still changing by ~1e-6 Ang^2 per step (my dis_conv_tol 1e-10 was too tight);
  this is converged for all practical purposes (lesson: use 1e-8 next time). The Wannierization took 1607 s, the kernel
  loop (ep-interp) only 95 s for 8064 k-points on 32 cores (~0.38 core-s per k-point) -> finer meshes are cheap.
  EPW read the PH dyn0 (1 1 1 grid), excluded 5 bands, window ibndmin..ibndmax = 1..17 (-5.6..18.4 eV), Ef = 6.40 eV read.
  EPW Gamma phonon energies: 25.199 meV (modes 4,5 = E_g), 25.781 (6,7 = E_u), 38.057 (8 = A_1g), 42.214 (9 = A_2u),
  i.e. 203.25 / 207.9 / 306.9 / 340.5 cm-1, matching DFPT+ASR to < 0.1 cm-1.
  Kernel on 24x24x12 (scripts/kernel_invariants.py -> run/04_epw/k24x24x12/kernel_k24_peaks.txt): largest Frobenius
  invariant is mode 8 (A_1g, 9.202 THz) at 4.04 eV, 73.4 Ang^2/eV; E_g modes peak at 5.90 eV (14.4); E_u and A_2u are
  ~0.1 (numerically zero) -- expected: in a centrosymmetric crystal only even (Raman-active) modes have a nonzero
  second-order kernel; this is a consistency check of the calculation and of the sign conventions.
- 23:55 Submitted: EPW run 2 (36x36x18, 48x48x24, 60x60x30 sequentially, small, 64 tasks), EPW run 3 (72x72x36 and
  96x96x48 on one full standard node, in run/04_epw_b with copies of the .fmt files, reading the same epmatwp), and the
  pw.x bands run on the 360-point Wannier90 path (G-M-K-G-A-L-H-A). Rationale for going to 96x96x48: with eta = 25 meV
  and band velocities of a few eV*Ang, the k-spacing energy at 60x60x30 is ~0.09 eV, so the peak may still move.
- 00:35 Results of the first mesh series (v1 WFs). EPW run 2 (36/48/60) had failed instantly because I had never copied
  its three input files to LUMI (error "open_input_file: fatal error opening epw_k36x36x18.in"; 7 s of a shared node);
  resubmitted as job 22848335. EPW run 3 on a full standard node worked: 72x72x36 in 11 m 46 s, 96x96x48 in 27 m 44 s
  (kernel loop 688 s and 1641 s on 128 cores). Invariant maxima (Frobenius, scripts/kernel_invariants.py):
    mesh        mode 8 (A_1g) peak      value      mode 4/5 (E_g) peak   value
    24x24x12    4.04 eV                 73.4       5.90 eV               14.4/14.2
    72x72x36    4.02 eV                 53.2       5.66 eV               13.4/13.2
    96x96x48    4.10 eV                 53.1       5.64/5.66 eV          13.3/13.1
  The A_1g spectrum is a broad plateau 3.9-4.2 eV (45-53 Ang^2/eV); 72 and 96 agree point by point within ~2-5 %, the
  maximum's position moves inside the plateau. Decision: add 120x120x60 to pin the position (cost ~0.75 node-h).
  Inversion-odd modes (E_u, A_2u) stay at ~0.05-0.1, i.e. zero within noise, on all meshes.
- 00:40 Wannier quality v1 (run/05_bands/bands.out = DFT on the 360-point Wannier90 path, run/04_epw/sns2_band.dat =
  Wannier-interpolated; scripts/compare_bands.py, nearest-band matching): window [-9, 13.2] eV (all valence + conduction
  up to CBM+6.0 eV): RMS 1.38 meV, max 28.2 meV at 13.19 eV. By energy bin: <= 1.1 meV max up to 9 eV, 2.2 meV to 11 eV,
  5.9 meV to 12.5 eV, 12.2 meV to 13.0 eV, 28 meV in 13.0-13.2 eV -- the degradation is the edge of the frozen window
  (13.5 eV). Decision: v2 Wannierization with dis_froz_max = 14.3 eV (band 20 starts at 14.58 eV, so at most 14
  non-semicore bands are frozen anywhere, 17 WFs suffice), dis_win_max 26 eV, dis_conv_tol 1e-7 (v1's 1e-10 never
  triggered), epbwrite off (fewer files). Jobs 22848481 (Wannierize + k48) and 22848482 (72/96/120 on one standard node,
  chained). The v1 epmatwp is kept as sns2.epmatwp.v1; the v1 .epb files are deleted (file-count quota).
- 02:45 (Oct 15) v1 mesh series complete (run/04_epw/convergence_v1.txt): A_1g maximum 73.4 (k24), 58.1 (k36), 56.1 (k48),
  57.1 (k60), 53.2 (k72), 53.1 (k96) Ang^2/eV at 4.04/3.94/4.06/4.08/4.02/4.10 eV. The plateau 3.9-4.2 eV is resolved
  from k60 on; values at fixed photon energies agree between k72 and k96 to within ~1-4 Ang^2/eV (2-8 %) point by point.
- 02:45 v2 Wannierization REJECTED (run/05_bands/wannier_vs_dft_v2.txt, run/04_epw_v2/sns2.wout): with the frozen window
  raised to 14.3 eV the disentanglement converged to a much worse solution: total spread 59.45 Ang^2 (v1: 37.64), band
  deviations RMS 36 meV and max 393 meV at 1.7 eV (inside the valence bands), and spurious non-zero kernels for the
  inversion-odd modes (E_u up to 5 Ang^2/eV at 2.3 eV). Interpretation: freezing free-electron-like states up to 14.3 eV
  cannot be localized by Sn spd + S sp projections; the WFs delocalize and the Fourier interpolation degrades everywhere.
  Its 120x120x60 run was cancelled (job 22848482, 1.1 node-h spent on v2 in total, not used).
- 02:50 Kept v1 (RMS 1.4 meV over [-9, 13.2] eV). Launched (a) the v1 120x120x60 kernel on a standard node, reading a
  separate copy of the v1 Wannier-basis e-ph file (03_nscf/tmp_v1) so that nothing can overwrite it (job 22852082);
  (b) one more Wannier trial v3 (frozen top 13.9 eV, dis_mix_ratio 0.5 = W90 default, job 22852083). If v3 is not better
  than v1 on the band comparison, v1 stays final.
- 03:40 (Oct 15) Final runs in. v1 kernel on 120x120x60 (job 22852082, 51 m 35 s on one standard node, kernel loop 3054 s):
  A_1g maximum 53.74 Ang^2/eV at 4.08 eV; 96x96x48 gave 53.12 at 4.10, 72x72x36 53.20 at 4.02. Smoothed (+-0.05 eV)
  peak 4.06 eV / 51.6-51.8 for all three (run/04_epw/smoothed_peaks_v1.txt). E_g maxima 13.29/13.15 at 5.66 eV on all
  meshes from 36x36x18. Convergence table: run/04_epw/convergence_v1.txt. Adopted mesh 120x120x60.
- v3 Wannier trial (job 22852083, frozen top 13.9 eV, dis_mix_ratio 0.5) REJECTED like v2: total spread 57.6 Ang^2,
  bands RMS 67 meV, max 0.92 eV (run/05_bands/wannier_vs_dft_v3.txt). Its 48x48x24 kernel (52.0 at 4.04 eV) is only kept as
  a record. Lesson: for this system the 17-WF Sn spd + S sp model is well localized only when the frozen window stops
  ~0.3-0.4 eV above the CBM+6 eV comparison window (13.5 eV); pushing it higher drags in free-electron-like states.
- Clean-up on LUMI: all pw.x wavefunction files (SCF, NSCF, bands), the coarse .epb files, the v2/v3 epmatwp and the
  duplicate v1 epmatwp, dmedata/chk/mmn/hr of v2/v3 deleted; remote root now 2.2 GB (the final v1 Wannier-basis e-ph file
  sns2.epmatwp, 1 GB, is kept in run/03_nscf/tmp_v1 in case the kernel has to be re-run on another mesh).
- Compute: 4.72 node-hours counted conservatively with allocated hardware threads (3.67 per physical core); 2.2 node-hours
  for the adopted chain. Far below the 20 node-hour cap. Wall-clock used: ~5.5 h.
- Deliverables written: REPORT.md (final), jobs.log, this file, DECISION.log/RUNNING.log, README.md (handoff), DONE.
