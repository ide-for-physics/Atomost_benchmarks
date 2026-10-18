# NOTES.md — InPS4_mp20790 coherent-phonon generation kernel (cophon-bench v1, whiteboard arm)

Running log of what was done and decided, and why. Times are UTC unless marked EEST (LUMI local = UTC+3).

## 0. Situation at the start of the 2026-10-17 session (recovery)

- Earlier sessions of this task (2026-10-16, ~01:30 UTC onwards) did most of the pipeline on LUMI but left no
  NOTES.md / jobs.log locally and their transcripts were lost (the only surviving transcript, 2026-10-17 04:05 UTC,
  shows a session that re-read the papers and the toolchain and then hit the account usage limit).
- Everything on the cluster is intact under the remote root
  `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/InPS4_mp20790/`
  (`inputs/`, `jobs/`, `logs/`, `run/{scf,nscf,bands,ph,epw_48,epw_72,epw_bands}`, `tmp*`). I verified every step's
  output before reusing it (section 2) and reconstructed `jobs.log` from `sacct`.
- Start time of the whole task (for `wall_hours`): the first remote activity is 2026-10-16 05:05 EEST = 02:05 UTC;
  the launcher comment ("10-16 18:3x", second account) is consistent with a launch at 2026-10-15 18:3x PDT =
  2026-10-16 01:3x UTC. I take the start as 2026-10-16 01:35 UTC (uncertainty ~30 min).

## 1. Physics / method decisions (from papers/ and the EPW source in the toolchain)

- Kernel: Gamma^{ab}_s(omega_s; omega, -omega), Eq. (Gamma_2nd_final) of the manuscript; implemented in the
  toolchain's `EPW/src/indabs.f90` as `Gamma_alphabeta_s` (triangle diagram "Gamma_c", using `epf17` (g) and
  `vmef` (h); the g^{s;a} vertex (diagram e) is marked "out of scope in v1" in that source). It is switched on by
  `lindabs = .true.` and written at the last q-point to `Gamma_alphabeta_s.dat`:
  header lines, then per optical mode (`imode = 4..nmodes`, phonon energy in meV), rows
  `omega(eV) Re,Im of xx yy zz xy xz yz yx zx zy` in Å²/eV. `Pi_0.dat` (phonon self-energy) is written alongside.
  The omega = 0 row is NaN by construction (1/omega² prefactor) and is excluded from the analysis.
- Photon grid: `omegamin=0, omegamax=6, omegastep=0.05` eV (121 points). Broadening `degaussw = 0.025 eV` as in the
  paper's SI ("electronic broadening eta = 0.025 eV"); the phonon-resonant denominator uses the same degaussw.
  `ladsmear = .false.` (fixed smearing, as in the paper), `temps = 300`, `efermi_read = .true.` with
  `fermi_energy = 5.7164 eV` = mid-gap (VBM 4.5773, CBM 6.8554 eV from scf/nscf). `fsthick` default (all 24 bands).
- "Rotational invariant" reported in RESULT.json: per mode and photon energy I use
  S1_s(omega) = sum_{ab} |Gamma^{ab}_s(omega)| over the 9 Cartesian channels ("per-mode magnitudes summed over
  Cartesian channels", task sheet). The Frobenius norm sqrt(sum_{ab}|Gamma^{ab}|²) is reported in REPORT.md as well;
  both peak at the same photon energy and mode.
- Cell: sealed cell of structure.cif used exactly (CELL_PARAMETERS from structure_POSCAR). Internal coordinates not
  relaxed: the scf forces on the given positions are <= 3.4e-5 Ry/bohr (total force 1e-4), i.e. the structure is
  already at equilibrium for PBE at this cell; pressure 18.9 kbar (cell is sealed, irrelevant).
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (In, P, S) used scalar-relativistically (no SOC), as allowed.
  ecutwfc = 80 Ry, ecutrho = 320 Ry (NC). 42 valence electrons, 21 occupied bands, nbnd = 40.
- Symmetry: space group I-4 (No. 82), point group S4 (ph.x: 4 sym. ops., no inversion). Gamma optical irreps A, B, E
  (E = complex-conjugate pair E/E*, printed by ph.x as degenerate pairs).

## 2. Pipeline on LUMI (all inputs in inputs/, Slurm scripts in jobs/, compute in jobs.log)

1. scf (job 22887425, debug): 6x6x6 MP grid, conv_thr 1e-12, diago_thr_init 5e-6 (build quirk). Converged in 12
   iterations, E = -235.13538538 Ry, gap 2.278 eV (PBE), forces ~3e-5 Ry/bohr.
2. DFPT (job 22887429, small, 2.39 node-h): ph.x `ldisp` on a 3x3x3 q-grid including Gamma, tr2_ph 1e-16, dvscf
   written (`fildvscf`). Only the Gamma q-point is needed by the kernel (nq = 1x1x1 in EPW), the other q-points were
   computed by the earlier session; they are kept as run/ph/inps4.dyn2-6 but not used.
   Gamma frequencies (DFPT, before ASR): acoustic 4.4/5.1/5.1 cm-1, optical 83.86(E) 109.90(B) 147.55(A) 169.47(E)
   244.90(B) 262.63(A) 310.61(B) 319.11(E) 398.80(A) 500.38(B) 537.65(E) cm-1.
   ASR (dynmat.x, asr='crystal', phonons/dynmat_gamma.out): acoustic -> 0.00, optical 83.89(E) 109.93(B) 147.55(A)
   169.48(E) 244.90(B) 262.63(A) 310.61(B) 319.10(E) 398.80(A) 500.38(B) 537.65(E) cm-1; ||dyn(ASR)-dyn|| = 2.6e-4.
   EPW imposes its own ASR on the dynamical matrix ("Imposing acoustic sum rule on the dynamical matrix"); the mode
   energies it writes in the kernel file (e.g. mode 11: 32.553 meV = 262.56 cm-1 = 7.871 THz) agree with dynmat.x to
   < 0.1 cm-1.
3. nscf (job 22887430): full 6x6x6 grid, 216 explicit k-points in [0,1) (EPW requirement), nosym/noinv, nbnd 40.
4. DFT bands (job 22887493): 83 k-points on the closed path (0,0,0)-(1/2,0,0)-(1/2,1/2,0)-(0,1/2,0)-(0,0,0)-
   (0,0,1/2)-(1/2,0,1/2)-(1/2,1/2,1/2)-(0,1/2,1/2)-(0,0,1/2) in reduced coordinates of the primitive reciprocal
   lattice (path.dat, step 0.05), nbnd 40.
5. EPW kernel runs (jobs 22889837 = 48³ on 1 node, 22890934 = 72³ on 2 nodes). Each run re-does the Wannierization
   from scratch (deterministic: identical spreads to 1e-5 Å² in both runs) and the coarse e-ph matrix, then the fine
   interpolation. Wannier setup: 24 WFs = s+p projections on all 6 atoms; dis_win [-4.5, 15.0] eV, frozen
   [-1.0, 12.9] eV (absolute energies); 12 valence bands (P-3s band at -4.1 eV + 11 S-3p bands) + lowest conduction
   bands. Final spread 98.4 Å² (Omega_I 73.8).
6. 96³ run: `inputs/epw_kernel_96.in` (only nkf changed), job 22927673, 4 nodes x 128 ranks (npool = nranks), 3 h
   limit, partition small. Submitted 2026-10-17 06:36 UTC; `sbatch --test-only` predicted start 13:27 UTC for
   small (both 2- and 4-node shapes) vs 2026-10-18 18:25 UTC for standard, so small was chosen.
   Expected cost ~4 node-hours (ep-interp scaled from 1292 s on 128 ranks at 48³ and 2914 s on 256 ranks at 72³).

7. 08:41 UTC: the queue on small worsened (new submissions now predicted to start 2026-10-18 00:00 UTC for any
   1/2/4-node shape; standard 2026-10-18 18:25 UTC). To exploit backfill I submitted a 1-node 4 h backup copy of
   the same run (job 22929556, `jobs/epw_kernel_job96b.sh`): at start it cancels the 4-node job if that is still
   pending and exits immediately if the 4-node job already runs/finished, so there is never a double run or a
   clobbered run directory. Whichever starts first is used; the other is cancelled (no compute charged).

## 3. Verification of the recovered results (2026-10-17)

- Wannier quality (scripts/analyze_bands.py; data in wannier/): Wannier bands interpolated from `inps4_hr.dat` +
  `inps4_wsvec.dat` (use_ws_distance) on the 83-point path vs pw.x bands:
  valence bands (12, all in the manifold): RMS 1.37 meV, max 6.9 meV;
  conduction bands up to CBM+3 eV: RMS 2.3 meV, max 11.6 meV; up to CBM+4.5 eV: RMS 3.1 meV, max 19 meV;
  up to CBM+6 eV: RMS 8.1 meV, max 63 meV (the largest deviations are at 12.3-12.8 eV, i.e. at the top edge of
  the frozen window where the Wannier manifold starts to disentangle). For photon energies <= 6 eV the resonant
  conduction states lie below VBM + 6 eV = 10.6 eV (CBM + 3.8 eV), where the agreement is 2-3 meV RMS.
  Decision: accept; a re-Wannierization would not change the kernel measurably and would cost another EPW chain.
  (The earlier `epw_bands` attempt with elph=.false. produced no band.eig because EPW stops after Wannierization
  when elph is false; the hr.dat route gives the same information.)
- Kernel 48³ vs 72³ (scripts/analyze_kernel.py): the largest invariant is mode 11 (A, 32.55 meV, 7.871 THz) at
  3.10 eV: S1 = 114.19 (48³) -> 114.78 Å²/eV (72³), +0.51 %; Frobenius 61.35 -> 61.66 Å²/eV. Second: mode 7
  (A, 18.29 meV) at 3.05 eV, S1 = 84.1; third: mode 15 (A, 49.44 meV) at 5.25 eV, S1 = 66.3. The whole spectrum of
  mode 11 changes by < 1 % between the meshes at every 0.25 eV sample from 2.5 to 6 eV. All three dominant modes are
  fully symmetric A modes with xx ~ yy ~ zz channels, as expected for a Raman-like driving kernel in S4.
  The kernel vanishes below the gap (2.28 eV) as it must.

## 4. 96³ production run and closure (2026-10-17)

- Job 22927673 (4 nodes) started 10:24 UTC (3 h 48 min after submission, far earlier than the 13:27 UTC estimate)
  and finished 11:11 UTC: 47:41 wall, 3.18 node-hours (ep-interp 2702 s on 512 ranks). The 1-node backup
  (22929556) started 16 s later, found the other job running and exited (3 s). Output clean (same generic
  "Wannier bands might differ near Ef" note as before; identical Wannier spreads).
- Convergence (scripts/analyze_kernel.py on 48/72/96): peak S1 of mode 11 at 3.10 eV = 114.191 / 114.777 / 114.737
  Å²/eV (+0.51 %, −0.035 %); Frobenius 61.353 / 61.662 / 61.639. Same peak energy and mode on all meshes; all
  per-mode maxima agree 72³→96³ to ≤ 0.1 % (0.7 % for the weak mode 6). Decision: adopt 96³ as the production mesh
  (`kernel/Gamma_alphabeta_s.dat`), no 120³ run needed; the remaining budget (11.4 node-h) is left unused.
- RESULT.json written by scripts/write_result.py from the production kernel file and jobs.log:
  peak_ev 3.10, peak_a2_per_ev 114.737, mode 7.8713 THz (32.553 meV), irrep A, mesh 96x96x96, 8.59 node-hours.
- Scratch cleanup (own root only): deleted nscf/scf/bands wavefunctions, EPW .epb/.epmatwp intermediates,
  the q≠Γ DFPT subdirectories tmp/_ph0/inps4.q_2..6 (their dyn files are kept in run/ph), and the 190 MB .mmn
  overlap files; kept the Γ dvscf, charge densities, all text outputs and the kernel files.
  Remote footprint now ~1.1 GB (tmp 371 MB, run 683 MB).
- Not done / caveats: no EPW `band_plot` cross-check job (the hr.dat route gives the same Wannier interpolation);
  internal coordinates not relaxed (forces already ~1e-5 Ry/bohr); PBE gap without correction.
