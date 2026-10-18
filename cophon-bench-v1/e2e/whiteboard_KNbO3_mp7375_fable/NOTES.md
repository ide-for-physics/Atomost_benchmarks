# NOTES — KNbO3_mp7375 coherent-phonon generation kernel (cophon-bench v1, whiteboard arm, model fable)

Start: 2026-10-16 22:27 UTC (container start; first command). All times UTC.

## 0. Reading of the papers / code (what is actually computed)

* Manuscript Eq. (Gamma_2nd_final): second-order kernel Gamma^{ab}_s(omega_s; omega, -omega), diagrams (c) [triangle:
  two velocity vertices + one EPC vertex] and (e) [one velocity vertex + covariant derivative of EPC].
* Implementation note + source `EPW/src/indabs.f90` of the toolchain build (qe-phnlo-75): the active "kernel variant"
  computes ONLY the triangle diagram Gamma_c (plus the field-free phonon self-energy Pi_0); Gamma_e (g^{s;a}) is declared
  (`lgammae`) but "out of scope in v1". Gaussian delta functions of width `degaussw` for the electronic resonance,
  1/(w_s + eps_lj + i*degaussw) for the phonon-resonant denominator, prefactor i*pi/omega^2, units ang^2/eV.
* Trigger: `lindabs = .true.` (phonon-assisted-absorption driver re-used), photon grid `omegamin/omegamax/omegastep` (eV),
  `degaussw` (eV), `temps`, optional `ladsmear` (adaptive smearing; off = paper setting). Output file written at the last
  fine q-point by the ionode: `Gamma_alphabeta_s.dat` with, per mode (imode = 4..nmodes) and photon energy,
  Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy. Also `Pi_0.dat`.
* The arrays are zeroed at every q-point call and written at the end, so the fine q-mesh MUST be the single point Gamma
  (nqf = 1x1x1): the kernel is a q = Gamma quantity anyway.
* The kernel uses `vmef` (velocity, `vme = 'wannier'`, default) and `epf17`, all bands in `nbndfst` (fsthick window around
  the Fermi level); occupation f_ij from etf vs ef0 => set `efermi_read = .true.` with a mid-gap Fermi level so that the
  valence/conduction assignment is unambiguous.
* `mp_mesh_k` must stay .false. (full fine mesh): the kernel is a Cartesian tensor and is not symmetrised by the code.
* SI, Methods: electronic broadening eta = 0.025 eV, PBE, SCF 1e-6 / ph 1e-16, 90 Ry cutoff for all materials;
  BaTiO3 (closest analogue, C3v) used 6x6x6 k and q; SnSe fine mesh converged at 256x256x1 (2D).
* "Rotational invariant" of the kernel used for RESULT.json (my reading of the task sheet + paper): per mode s and
  photon energy, I_s(w) = sum_{a,b} |Gamma^{ab}_s(w)| over the 9 Cartesian channels (the per-mode magnitudes summed over
  Cartesian channels). The peak is max over (s, w in [0,6] eV); the dominating mode is the s at that peak. This is written
  down in REPORT.md too so the grader can re-derive it from kernel/Gamma_alphabeta_s.dat.

## 1. Decisions

* Cell: sealed; use the POSCAR lattice vectors (3-fold axis along z, polarization along z as in the paper's BaTiO3
  convention). The CIF gives the same cell (a = 4.005020 A, alpha = 89.8916 deg). No vc-relax. Internal coordinates are
  relaxed at the fixed cell (needed so that DFPT at Gamma has no residual-force artefacts); the relaxed positions are
  reported in RESULT.json.
* Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (K 9e, Nb 13e, O 6e), used scalar-relativistically (no SOC).
  Dojo hints (normal): K 74, Nb 82, O 84 Ry -> ecutwfc = 90 Ry (also the paper's value), ecutrho = 360 Ry.
* Electrons: 40 valence electrons -> 20 occupied bands. Semicore ordering expected: Nb 4s, Nb 4p(3), K 3s, K 3p(3),
  O 2s(3) = 11 bands below the O 2p manifold (to be verified from the SCF eigenvalues).
* Coarse k-mesh 8x8x8 (SCF + NSCF full grid 512 points for EPW). Coarse q-mesh = Gamma only (1x1x1): the kernel needs
  g only at q = Gamma; with R_p = 0 only, the EPW phonon-side interpolation is exact at Gamma, the electron-side Wannier
  interpolation is the usual one. This saves the DFPT dispersion (would cost most of the 20 node-hour budget) and keeps
  the Gamma phonons exactly the DFPT ones (ASR applied by dynmat.x / EPW asr_typ = 'crystal').
* Fine meshes for the kernel: 24^3, 32^3, 48^3 (and 64^3 if time/budget allow); converged mesh = the one at which the
  peak changes by < ~5 %.
* degaussw = 0.025 eV (paper), ladsmear = .false., omegamin = 0.02 eV (omega = 0 is a 1/omega^2 singularity of the
  prefactor and produces 0*Inf = NaN rows), omegamax = 6.0 eV, omegastep = 0.02 eV.
* Remote root already contained an older tree (owned by the project owner, dated before this session). I do not read
  or reuse it; all my work is in the fresh sub-directory `fable_v1/` of the root.

## 2. Log

* 22:27 start. Read manuscript, SI (Sec. IV methods), implementation note; inspected `EPW/src/indabs.f90`, `input.f90`,
  `readin.f90`, `use_wannier.f90` of the toolchain (see Sec. 0). Queue check (LUMI 01:35 local): `sbatch --test-only`
  gives start times: debug immediately, small ~6 h, standard ~41 h (569 / 532 pending jobs). All my steps are
  short (5-atom cell), so the quick steps go to debug one at a time (< 10 min each); long kernel runs to small/standard
  depending on the test-only estimate at that moment.
* Job 22922824 (debug, 32 cores): SCF at the sealed cell, 8x8x8 k, 90 Ry: 9 s wall, converged with conv_thr 1e-10
  (Davidson did not abort here). 6 symmetry ops (C3v) found. PBE gap: VBM 8.4109 eV, CBM 10.6171 eV (2.206 eV on the
  8x8x8 grid). Forces at the Materials-Project positions < 4e-5 Ry/Bohr, i.e. already below any sensible relaxation
  threshold -> NO internal relaxation performed; positions used as given. Pressure 50 kbar (cell is sealed, irrelevant).
  Gamma eigenvalues (eV): -46.2 (Nb 4s), -22.4 x3 (Nb 4p), -18.9 (K 3s), -8.6/-8.17 x2 (K 3p), -2.41 x3 (O 2s),
  6.24..7.52 x9 (O 2p), 10.62 x2 / 10.84 (Nb t2g), 14.23 x2 (eg), 15.19, 16.54 x2, 19.48 x3, 23.98, ...
  => exclude_bands = 1-11; Wannier set O p + Nb d + Nb s + K s + K d (21 WFs), frozen window up to 17 eV (CBM + 6.4 eV).
* Job 22922838 (debug, 64 cores): SCF + ph.x at Gamma (ldisp, 1x1x1, tr2_ph 1e-16) + dynmat.x (asr crystal) + pp.py.
  ph.x 3m45s. Mode symmetry (ph.x, C_3v): acoustic E (-3.3 cm-1) + A1 (1.6 cm-1) before ASR; optical:
  E 183.15, A1 186.22, E 202.17, A1 237.30, A2 248.28, E 275.31, E 518.22, A1 570.91 cm-1 (dynmat.x, asr='crystal',
  acoustic -> 0.00). eps_inf = diag(5.584, 5.584, 5.181); Z*(K) ~ 1.17/1.15. `dynmat.x` warns "axis vectors are
  left-handed": the sealed POSCAR vector ordering (a1,a2,a3) has a1.(a2 x a3) < 0. QE/EPW use |volume| and the
  Cartesian frame is unchanged, so I keep the sealed ordering exactly as given (RESULT.json reports it as used).
  pp.py failed (it assumes outdir = './'); save/ assembled by hand: kno.dyn_q1, kno.dvscf_q1 (= _ph0/kno.dvscf1),
  kno.phsave/ — the same layout pp.py produces.
* Job 22922889 (debug, 64 cores): NSCF on the full 8x8x8 grid (512 k, 50 bands, nosym/noinv, diago_thr_init 5e-6)
  + DFT bands along G-X-M-G-R-X (pseudo-cubic labels, rhombohedral reciprocal basis) + projwfc.x. 1 min.
  Full-grid gap: VBM 8.4109 / CBM 10.6171 eV -> fermi_energy = 9.51 eV (mid-gap) for EPW. Window check on the 512 k:
  bands 12.. inside [2, 17.5] eV: at most 17 (<= 21 WFs, OK); inside [2, 30] eV: at least 27 (>= 21, OK).
  projwfc: the K pseudopotential carries no 3d atomic wavefunction, so the interstitial bands 27-31 (16.5-20 eV) have
  ~zero projection on the atomic basis; w90 hydrogenic K:d projections are used anyway as the initial guess.
* Job 22922922 (debug, 64 cores): epw.x wannierize (O:p, Nb:d, Nb:s, K:s, K:d; exclude 1-11; froz [2, 17.5] eV,
  outer [2, 30] eV; dis_num_iter 2000, num_iter 1000) + epwwrite + kernel on 12^3 as smoke test. 18 min (most of it
  w90 + writing epmatwp; ep-interp with kernel: 52 s for 27 k/pool, i.e. ~1.9 s per k-point per rank).
  Spreads: O p 0.65-0.72, Nb d 1.13-1.27, Nb s 2.29, K s 1.88, K d 1.94-2.24 A^2, total 26.77 A^2.
  DFT vs Wannier bands on G-X-M-G-R-X (DFT 'bands' run had an extra trailing X-R segment, dropped in the comparison):
  valence (9 O-2p bands) RMS 0.83 meV / max 6.9 meV; conduction up to CBM+6 eV RMS 1.84 meV / max 13.7 meV
  (up to CBM+4 eV: 0.98 / 5.3 meV). Good enough; kept.
  12^3 kernel: no NaN; peak of I_s = sum_ab |Gamma^ab_s| at 3.44 eV from mode 9 (A1, 237 cm-1), I = 128.9 A^2/eV
  (unconverged mesh). EPW's phonon energies on the fine mesh equal the dynmat.x ones (e.g. 29.42 meV = 237.3 cm-1).
* Production kernel runs (epwread, full node 128 ranks = 128 pools): 24^3 on debug (job 22923073, expected ~5 min);
  32^3 on debug after it; 48^3 (22923078) and 64^3 (22923079) submitted to `small` (test-only estimate: start ~07:04
  local = ~5 h wait; standard would start ~41 h later).
* 24^3 (22923073): 3m52s. 32^3 (22923107): 7m58s. Kernel cost scales linearly: ~0.9 s per k-point per rank incl.
  interpolation -> 48^3 ~27 min, 64^3 ~65 min on one node.
  Mesh behaviour of I_9(E) (mode 9, A1 237 cm-1, the dominant mode at every mesh): energy-integrated weight
  int_0^6 I_9 dE = 135.9 / 135.6 / 135.6 A^2 for 12^3 / 24^3 / 32^3 (converged), but the spectrum is a broad plateau
  between ~3.5 and ~4.0 eV whose point-wise maximum still moves: peak (E, I) = (3.44, 128.9), (3.84, 86.7),
  (3.74, 88.0). The 25 meV Gaussian needs the 48^3/64^3 meshes to settle the point-wise peak; decision rule: adopt
  the mesh at which the peak value changes by < 5 % and the peak energy by <= one 0.02 eV step (or sits on the same
  plateau feature) relative to the next-coarser mesh; otherwise run 80^3/96^3 (budget allows ~6 nh more).
* The `small` jobs started at 03:00 local (2 h earlier than the test-only estimate). 48^3 (22923078): 26m45s;
  peak (3.62 eV, 79.8); plateau values I_9(3.6/3.8/4.0 eV) = 79.0/74.7/67.6 vs 79.6/74.2/67.6 at 32^3 -> the plateau is
  converged to ~1 %, but the point-wise maximum still hops between 3.62 and 3.74 eV (values 79.8 vs 88.0, 9 % apart).
  64^3 (22923079) running since 03:00. Hedge: 96^3 queued on 2 nodes (22924174, job_kernel.sbatch now uses
  -npool $SLURM_NTASKS); will be cancelled if 64^3 agrees with 48^3 within the decision rule.
* 64^3 (22923079): 1h00m. Peak (3.66 eV, 80.43) vs 48^3 (3.62 eV, 79.76): value within 0.8 %, energy within 0.04 eV
  on the same broad maximum (I_9 >= 76.8 for 3.58-3.80 eV at 64^3). Point-wise |I64-I48|/max over 3-6 eV: mean 1.6 %,
  max 6-8 % (modes 6, 9, 15). Symmetry check at 64^3 for the A1 mode 9: xx = yy (25.98/26.00), zz 28.44, all
  off-diagonal channels < 0.03 -> consistent with C3v. CONVERGED by the decision rule at 64^3.
  I keep the queued 96^3 run (2 nodes, ~2 nh, budget used so far 1.85 nh) as an independent confirmation and will
  adopt it as the final kernel file if it completes and agrees (finest mesh); otherwise 64^3 is final.
* 96^3 (22924174, 2 nodes): started 04:52 local, 2h08m (slower than the linear estimate; Slingshot reported network
  timeouts but the run completed normally). Peak (3.64 eV, 79.97) vs 64^3 (3.66, 80.43): 0.6 % / one 0.02 eV step.
  ADOPTED 96^3 as the final kernel file (`kernel/Gamma_alphabeta_s.dat`); 64^3 kept as `..._64x64x64.dat`.
* Final numbers (RESULT.json): peak_ev 3.64, peak_a2_per_ev 79.9651 (I_9 = sum_ab |Gamma^ab_9|), mode 9 = A1,
  29.423 meV = 7.1144 THz (dynmat.x 237.30 cm-1). Compute 6.10 node-hours; wall ~5.8 h. No human touches.
* Cleanup: wavefunctions (nscf/scf/bands tmp) and the duplicate _ph0 dvscf deleted on the cluster; save/, EPW restart
  files (epmatwp, ukk, *.fmt) and all outputs kept under fable_v1/. Finished 2026-10-17 ~04:10 UTC.

## 3. Caveats worth knowing (for whoever compares against the reference)

* The build evaluates only the triangle diagram (c) of the second-order kernel (`lgammae` not implemented in this
  version); diagram (e) is therefore absent from the kernel file, as it is for any material computed with this code.
* The point-wise peak sits on a broad maximum (I_9 within 4 % of its peak over 3.58-3.80 eV); meshes >= 48^3 agree on
  the value to ~1 %, but the energy of the point-wise maximum can legitimately move by 0.02-0.04 eV between meshes.
* Coarse q-mesh = Gamma only (exact for the q = Gamma kernel; no phonon dispersion computed), lpolar = .false.
* The sealed POSCAR vector ordering is left-handed; kept as given (Cartesian frame unchanged).
