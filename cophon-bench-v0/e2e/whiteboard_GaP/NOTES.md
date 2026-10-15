# NOTES.md — running log, GaP coherent-phonon kernel (whiteboard arm)

Started 2026-10-14. Remote root: /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP/
Local root: <whiteboard>/GaP_whiteboard/

## 1. What the code actually computes (read from the LUMI source, EPW/src/indabs.f90)
- The coherent-phonon kernel is computed inside `indabs_main` (phonon-assisted-absorption module), i.e. it is
  switched on by `lindabs = .true.`. Photon grid: `omegamin`, `omegamax`, `omegastep` (eV). Smearing of the
  delta function: `degaussw` (Gaussian, w0gauss), optionally adaptive (`ladsmear`). Occupations: 0 K step at
  `fermi_energy` (`efermi_read = .true.`). Band window: `fsthick` around `fermi_energy`.
- Only the triangle diagram (Gamma_c of the paper, SI Eq. "diagram (c)") + Pi_0 is implemented ("v1 scope";
  the comment says Gamma_e with the EPC derivative g^{s;alpha} is out of scope in this build).
- Output file: `Gamma_alphabeta_s.dat`, written on the LAST q-point of the fine q loop, for modes 4..nmodes
  (optical modes). Columns: photon energy (eV), then Re,Im of xx, yy, zz, xy, xz, yz, yx, zx, zy, in ang^2/eV.
  Also `Pi_0.dat` (phonon self-energy, meV).
- The kernel uses `wf(imode, iq)` at the fine q-point, `epf17` (g) and `vmef` (velocity, vme='wannier' default).
  Modes with wf < eps_acoustic are skipped. Because the kernel is only meaningful at q = Gamma, the fine q grid
  is 1x1x1 (only Gamma), so "last q-point" = Gamma.
- No symmetry reduction can be used on the fine k mesh (the tensor is summed with plain weights): full grid.

## 2. Physics / parameter decisions
- Structure used exactly as given (ibrav=0 with the POSCAR vectors, Ga at 0, P at (1/4,1/4,1/4)) so the
  Cartesian orientation (and hence the sign/orientation of the polar tensor) matches the task file.
- PseudoDojo nc-fr-04 PBE standard (Ga with 3d semicore, 13 e; P 5 e), used scalar-relativistically
  (no spin-orbit), as allowed. ecutwfc = 90 Ry (Ga "high" hint 92 Ry, "normal" 80; paper used 90 Ry).
- SCF k-mesh 12x12x12; DFPT q-mesh 2x2x2 (Gamma, X, L irreducible), tr2_ph = 1e-16 (paper value), epsil=.true.
  (dielectric tensor + Born charges, needed for lpolar in EPW). Only q = Gamma enters the kernel and the
  Wannier interpolation reproduces the coarse-grid value at Gamma exactly, so the q-mesh size does not affect
  the kernel; 2x2x2 is used instead of 1x1x1 only to stay on EPW's well-trodden path.
- Gamma phonons with ASR: dynmat.x, asr='crystal', once without q-direction (TO triplet) and once with
  q=(1,0,0) (LO-TO split, non-analytic term).
- Coarse k-mesh for Wannier/EPW: 12x12x12 (commensurate with 2x2x2 q). NSCF nbnd = 32.
- Wannier: exclude the 5 Ga-3d bands; 18 Wannier functions (Ga s,p,d + P s,p,d) with a frozen window up to
  ~6 eV above the CBM so that the conduction bands needed for 6 eV photons are reproduced to a few meV.
  (To be adjusted after seeing the NSCF band energies.)
- Kernel: degaussw = 0.025 eV (the paper's electronic broadening, SI Sec. IV A), fixed (ladsmear = .false.),
  photon grid 0..6 eV step 0.01 eV, fermi_energy = mid-gap, fsthick = 7 eV (bands from VBM-6 to CBM+6 eV),
  fine k meshes: series (e.g. 48^3, 64^3, 80^3, ...) until the peak of the invariant is converged.
- "Rotational invariant": the papers do not name it explicitly; I take the per-mode Frobenius norm
  sqrt(sum_{ab} |Gamma^{ab}_s|^2) as primary (it is invariant under rotation of the Cartesian axes), and also
  report the plain sum of magnitudes sum_{ab} |Gamma^{ab}_s| and the quadrature sum over the three degenerate
  T2 modes, so that whichever definition the reference used can be matched.

## 3. Log
- 2026-10-14 ~12:40 Submitted job 22821757 (scf+ph+dynmat, small, 64 cores) and job 22821759 (bands + nscf,
  small, 128 cores, dependency afterok). Inputs: inputs/01_scf, 02_ph, 03_nscf, 04_bands.
- 13:29 Job 22821757 done (3m41s wall, 128 cpus): SCF converged in 11 iterations, 24 Td symmetry ops, E_tot = -166.83329957 Ry,
  VBM 7.6046 eV (Gamma), CBM 9.2019 eV (on the 12^3 grid, at X) -> PBE indirect gap 1.597 eV. Ga-3d bands at -6.95..-6.83 eV,
  sp3 valence band bottom -4.88 eV (Gamma). Stress 25.65 kbar at the given lattice constant (structure kept as given, not relaxed).
  DFPT: eps_inf = 10.539 (isotropic), Z*(Ga) = +2.147, Z*(P) = -2.156 (ASR violation 0.009). Gamma: raw DFPT acoustic -4.37 cm-1,
  optical T2 358.10 cm-1. With ASR 'crystal' (dynmat.x): acoustic 0.00, TO (T2, triply degenerate without the
  non-analytic term) 358.08 cm-1 = 10.7349 THz; with q->(1,0,0): TO 358.08 cm-1 (x2), LO 391.28 cm-1 = 11.7302 THz.
  Files: results/02_ph/{ph.out,dynmat_asr.out,dynmat_asr_q100.out,gap.dyn1,*.eig}.
- 13:30 Job 22821759 done (28 s): NSCF on the 12^3 grid (1728 k, 32 bands) + bands along G-X-W-K-G-L-U-W-L-K|U-X (387 k).
  Band statistics on the 12^3 grid: frozen window up to 15.5 eV (= CBM + 6.3 eV) contains at most 9 non-d bands; the 18th
  non-d band reaches 31.8 eV, so with 18 Wannier functions the outer window must extend to 32 eV. Decision: 18 WFs
  (Ga s,p,d + P s,p,d), exclude_bands 1:5 (Ga 3d), dis_win = [-6, 32] eV, dis_froz = [-6, 15.5] eV. Fallback if poor:
  13 WFs (Ga s,p,d + P s,p) with dis_win_max ~ 25 eV.
- 13:33 save/ built with EPW's pp.py (dvscf_q1..3, dyn_q1..3, phsave). Submitted job 3 (EPW wannierize + epb/epw write +
  band interpolation on the 387-point path with band_plot/filkf; small, 128 ranks, npool=128). inputs/05_epw/epw_wan.in.
- 14:24 Job 22822175 (18 WFs) done, 51 min wall of which 49 min was the serial Wannier90 step (5000 disentanglement +
  3000 Wannierization iterations at 1728 k-points) -> 0.85 node-h, more than it should have been. Result: the five Ga-"d"
  Wannier functions are diffuse (spreads 13-15 ang^2; they chase free-electron-like states up to 32 eV) and the
  interpolation is poor: along the 387-point path, VB+CB(<=CBM+6 eV) RMS 38.6 meV, max 376 meV (band CB1 between X and W),
  results/04_bands/wan18_band_compare.dat. Exact at coarse-grid points (checked at G, X, L) -> pure interpolation error.
  Band facts from bands.out: CB5 minimum 15.07 eV (along G-X, 0.4 of the way), CB4 reaches 18.2 eV at X, so the sp3
  antibonding manifold is entangled above ~14 eV; a frozen window up to 14.9 eV holds at most 8 bands.
- 14:40 Decision: five Wannier-only tests (elph=.false., 16 ranks each because W90 is serial): A 13 WFs (Ga s;p, P s;p;d,
  outer 25 eV, frozen 15.5); B 8 WFs (sp3+sp3, outer 20, frozen 14.9); C 9 WFs SCDM (erfc, mu 15.5, sigma 1.5, outer 22,
  frozen 15.5); D 13 WFs SCDM (mu 15.5, sigma 2, outer 25, frozen 15.5); E 8 WFs SCDM (mu 14.9, sigma 1.5, outer 20,
  frozen 14.9). Quality metric: W90 band plot on G-X-W-K-G-L (228 points, coincides with the DFT path points) vs DFT,
  scripts/parse_w90bands.py. The chosen set will then be used in a full elph run with wannierize=.false. (reads gap.ukk).
- 15:05 (local) The five small-partition tests have been pending >80 min (cluster saturated: 566 pending on small, 350 on
  standard, ~1% idle). Hedge: backup job 22829316 on standard (1 node, 5 concurrent 16-rank steps); a poller cancels
  whichever copy has not started when the other starts, so no test runs twice (worst case one overlap).
- 16:10 Five Wannier tests done (results/wannier_tests/, scripts/summarize_wan_tests.sh). W90 band plot vs DFT on the
  228-point G-X-W-K-G-L path (VB + CB <= CBM+6 eV):
    A 13 WFs proj (Ga s;p, P s;p;d): RMS 126 meV, max 1.65 eV  -> rejected (diffuse d-like WFs again)
    B  8 WFs sp3+sp3 (frozen 14.9):   VB RMS 2.0 meV, but CB3/CB4 RMS 68/189 meV, max 0.72 eV -> rejected
    C  9 WFs SCDM (erfc mu 15.5, sigma 1.5, outer 22, frozen 15.5): ALL RMS 11.6 meV; VB 1.8 (max 8.5); CB1 3.9, CB2 5.4,
       CB3 6.3, CB4 12.1 meV RMS (max 47 meV); CB5 only enters the window at 8 points near its 15.07 eV minimum and is
       off by ~150 meV there (9th WF has spread 9.1 ang^2)  -> best candidate
    D 13 WFs SCDM (mu 15.5, sigma 2): ALL RMS 13.8 meV, max 90 meV, VB 6.9 meV -> worse than C in the VB and CB1-2
    E  8 WFs SCDM (mu 14.9, sigma 1.5): like B, CB3/CB4 bad -> rejected
  Decision: use C now for the electron-phonon (elph) run with wannierize=.false. (job 22831204, reads wan_C_s9/gap.ukk,
  band_plot on the 387-point path for the definitive comparison), and in parallel try F (9 WFs SCDM mu 15.0 sigma 1.0) and
  G (10 WFs SCDM mu 16.0 sigma 1.5, outer 24) (jobs 22831205/6), plus an NSCF on a 16^3 coarse grid (job 22831207, run16/)
  so that the final set can be re-Wannierized on a denser coarse mesh if the few-meV target is not met on 12^3.
- 16:30 Tests F and G done. F (9 WFs, mu 15.0, sigma 1.0): VB 1.0 meV, CB1-4 3-8 meV RMS, but CB5 still ~200 meV off at its
  minimum. G (10 WFs SCDM, mu 16.0 eV, sigma 1.5 eV, outer window 24 eV, frozen 15.5 eV): all spreads 2.2-2.8 ang^2,
  RMS 4.3 meV over VB+CB<=CBM+6 (VB 1.4 meV max 5.6; CB1 2.1, CB2 2.8, CB3 4.3, CB4 6.6 meV RMS, max 28 meV; CB5 47 meV
  RMS at the 8 points where it dips below CBM+6). CHOSEN: set G.
  The elph run with set C failed: EPW (readin.f90 line 916) overwrites filukk with prefix.ukk, so the ukk must be in the
  working directory; the elph runs are now executed inside the Wannier directories (wan_G_s10/, wan16_G_s10/) where
  gap.ukk and gap.mmn (needed for vme='wannier') already exist. Jobs: 22831586 (elph G 12^3), 22831587 (24^3 kernel
  timing test, chained), 22831592 (G on 16^3) + 22831593 (elph G 16^3, chained). The 16^3 coarse mesh is tried because the
  remaining errors (CB4/CB5 near 15 eV) are interpolation errors that shrink with a denser coarse mesh.
- 18:40 Set G on the 16^3 coarse mesh (job 22831592): spreads 2.2-2.9 ang^2, band interpolation on the 228-point path
  RMS 1.3 meV (VB 0.4 meV max 1.8; CB1 0.7, CB2 1.0, CB3 2.1, CB4 2.8 meV RMS, max 18.7 meV; CB5 7.8 meV at its 8 points).
  -> PRODUCTION: set G, 16^3 coarse k, 2x2x2 coarse q.
  The elph run with set G on 12^3 (22831586) crashed reading save/gap.dyn_q3: the authors' modified
  ep_coarse_unfolding.f90 reads prefix.dyn0 from the CURRENT directory to recover the ph.x irreducible-q order
  (Gamma, L, X); without it, the fallback order is wrong and the X file is parsed as an L point ("Bad integer" runtime
  error). Fix: gap.dyn0 copied into wan_G_s10/ and wan16_G_s10/ (verified that run/ had it, which is why the 18-WF run
  worked). The 16^3 elph job 22831593 is still pending so it will pick the file up; the 24^3 timing test is now chained
  to it (k24, coarse 16^3).
- 19:35 Job 22831593 (elph, set G, 16^3 coarse) done in 3m41s: gap.epmatwp written (820 MB); EPW-interpolated bands on
  the full 387-point path vs DFT (results/04_bands/wanG16_band_compare.dat): RMS 1.67 meV, VB 0.31 meV (max 1.4),
  CB <= CBM+6 eV 2.47 meV (max 20.2 meV at one point of CB4 near 15 eV). fsthick window [1.41, 15.39] eV selects
  bands 2-9 of the 10-band model (nbndfst = 8).
  Job 22835783 (24^3 timing test) done: 20.5 s wall on 128 ranks for 13824 k -> ~0.1 core-s per fine k-point
  (ep-interp 11.4 s). 24^3 kernel: three degenerate T2 modes at 44.400 meV = 10.7358 THz (= dynmat TO), kernel
  tensors dominated by the Td-allowed off-diagonal (xy-type) entries, diagonal entries ~1e-2 (noise), per-mode Frobenius
  ~19.3 ang^2/eV at ~2.8 eV, total in quadrature 33.35 (unconverged mesh).
  Production series submitted (set G 16^3 coarse, degaussw 25 meV, 0.01-6 eV step 0.01): 48^3, 72^3, 96^3, 120^3, 144^3
  (jobs 22838842-46, small, 128 ranks each). Scratch cleanup: 12^3 wavefunctions, epb and epmatwp of the 18-WF run deleted.
- 20:50 Production meshes 48^3..144^3 done (jobs 22838842-46; 1.6, 5.2, 12.1, 22.4, 39.0 min on 128 ranks).
  Mesh convergence of the total invariant (quadrature over the three T2 modes) and its peak (scripts/mesh_convergence.py,
  results/kernel/mesh_convergence.dat):
    N    peak E (eV)  peak total (ang^2/eV)  per-mode Frobenius at peak
    48   2.87         17.42                  10.08
    72   2.81         17.84                  10.32
    96   2.81         17.39                  10.06
    120  2.81         17.46                  10.09
    144  2.81         17.67                  10.22
  Peak energy converged at 2.81 eV from 72^3; peak value fluctuates by +-1.5 % between 96^3 and 144^3 with a slight
  upward drift (25 meV Gaussian smearing on a 144^3 mesh gives an energy spacing of ~50 meV along the steepest bands).
  The 2.81 eV peak coincides with the E1 critical point of GaP (L3v -> L1c = 9.28 - 6.49 = 2.79 eV in PBE here).
  Submitted 168^3 (1 node) and 192^3 (2 nodes, 256 ranks) to settle the last percent.
  Accounting note: sacct reports NCPUS as hyperthreads (256 for 128 tasks); jobs.log lists the conservative value
  NCPUS x elapsed / 128 and, in brackets, the physical-core value (= elapsed hours for a full 128-core node).
- 22:05 168^3 (job 22842951, 62 min, 1 node) and 192^3 (job 22842952, 47 min, 2 nodes) done. Peak total 17.61 / 17.61
  ang^2/eV at 2.81 eV (144^3: 17.67): changes -0.3 % and -0.02 %. Per-mode Frobenius 10.16-10.18 ang^2/eV. CONVERGED.
  Adopted: 192^3 for the reported numbers; 144^3/168^3/192^3 as the convergence evidence. Total compute 9.3 node-h
  conservative (hyperthread count) = 4.7 node-h by physical cores; budget 20.
  Remote cleanup: deleting the 16^3 coarse wavefunctions (run16/gap.save/wfc*, 4096 files), run_bands wavefunctions,
  epb files; keeping gap.epmatwp (820 MB) and all inputs/outputs. REPORT.md finalized; DONE written.
- 22:15 Final remote cleanup (per-process pw.x/EPW wavefunction scratch gap.wfc* in run/, run16/, run_bands/ deleted;
  kept: inputs, outputs, save/ (dvscf, dyn), wan16_G_s10/gap.epmatwp + ukk + mmn so the kernel can be re-run from
  the Wannier data without recomputing DFT). Deliverables complete: REPORT.md, jobs.log, inputs/, results/, NOTES.md.
  Known limitations stated in REPORT.md: only the triangle diagram (c) + Pi_0 is implemented in this build of the
  kernel variant (no Gamma_e term), PBE gap (no scissor), no spin-orbit, LO-TO splitting absent at exactly q = Gamma.
