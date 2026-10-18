# NOTES — NbFeSb_mp9437 coherent-phonon kernel (cophon-bench v1, whiteboard)

Start of session (container clock): 2026-10-16 ~18:45 (folder created 18:45).

## 0. Reading / decisions before computing
- Kernel: manuscript Eq. (5) (second-order light-induced coherent-phonon kernel
  Gamma^{ab}_s(w_s; w, -w)). The authors' EPW "kernel variant" implements only the
  triangle diagram (c) (`Gamma_c`) in `EPW/src/indabs.f90` (subroutine `indabs_main`):
  accumulated on the fine k grid with Gaussian deltas of width `degaussw`, prefactor
  i*pi/w^2, 1/sqrt(2 w_s), units converted to ang^2/eV; written to `Gamma_alphabeta_s.dat`
  (modes 4..nmodes; columns: w(eV), Re/Im of xx,yy,zz,xy,xz,yz,yx,zx,zy) at the LAST fine
  q point. The (e) diagram with g^{s;a} is not in this build. The kernel divides by w^2, so
  omegamin must be > 0.
- Inputs needed by the kernel: lindabs=.true., omegamin/omegamax/omegastep (eV), degaussw (eV),
  optional ladsmear (adaptive interband smearing), eps_acoustic, fsthick (only selects the
  bands kept: keep it large to include all Wannier bands), efermi_read/fermi_energy, temps.
  vme='wannier' so that vmef = h^a_mn as in the implementation note.
- Only q = Gamma is needed -> DFPT on a 1x1x1 q mesh (Gamma only, with epsil for Z*/eps),
  EPW nqf = 1x1x1, fine k mesh converged. The modified `ep_coarse_unfolding.f90` reads
  prefix.dyn0 in the run directory for the irreducible-q order -> copy dyn0 there.
- Electronic broadening in the paper: eta = 0.025 eV (SI, Methods). Used as degaussw.
- The remote root already contained a previous attempt's files (`run/`, `pp/`, `logs/`, owned
  by <user>, dated Oct 15-16). Task says "from scratch": I do not read or reuse them; all my
  work is in the fresh subdirectory `v1/` of the root.
- Pseudopotentials: PseudoDojo nc-fr-04 pbe standard (Nb 13e, Fe 16e, Sb 15e -> 44 e, 22 occupied
  bands). Hints (normal): Nb 82, Fe 90, Sb 80 Ry -> ecutwfc = 90 Ry, ecutrho = 360 Ry.
  Scalar-relativistic use (no SOC, lspinorb=.false.), allowed by the task sheet.
- Cell: sealed fcc cell, a_conv = 5.8937838 A (primitive vectors (0,2.9468919,2.9468919) etc.),
  Nb (0,0,0), Fe (1/4,1/4,1/4), Sb (1/2,1/2,1/2): space group F-43m (216), point group Td.
  All Wyckoff positions are fixed by symmetry -> internal relaxation is a no-op (forces are
  zero by symmetry; verified in the SCF output). No vc-relax (cell sealed).
- Td point group: 3 atoms -> 9 modes; optical modes at Gamma: 2 x T2 (triply degenerate, IR+Raman).
  For the second-order kernel, the only Td-invariant rank-3-like coupling is of xyz type, so a
  z-polarized T2 component couples to Gamma^{xy} = Gamma^{yx}; diagonal components vanish.
- "Rotational invariant" used for RESULT.json: per mode s and photon energy, the sum over the 9
  Cartesian channels of |Gamma^{ab}_s| (per-mode magnitudes summed over Cartesian channels).
  The Frobenius norm sqrt(sum |Gamma^{ab}|^2) is reported in REPORT.md as well.

## 1. DFT ground state (jobs 22919868/22919896, scf.out)
- pw.x scf, 12x12x12 MP, ecutwfc 90 / ecutrho 360 Ry, fixed occupations, conv_thr 1e-10, diago_thr_init 5e-6.
- E_tot = -557.11805314 Ry; 24 symmetry operations (Td); forces exactly zero; stress +62.6 kbar
  (sealed cell is slightly compressed w.r.t. PBE equilibrium; cell kept as given).
- PBE gap on the 12^3 mesh: VBM 16.9722 eV, CBM 17.5050 eV -> 0.533 eV (indirect, consistent with literature).
- NSCF (8x8x8 uniform, 512 k in [0,1), nosym/noinv, 44 bands): bands 1-13 are semicore (Fe 3s/3p, Nb 4s/4p, Sb 4d;
  all below -11.7 eV); band 14 is Sb 5s (5.4-7.3 eV); bands 15-22 are the 8 upper valence bands; CBM = band 23.
  Bands with E <= CBM+6 eV: at most 30 -> 17 bands above the semicore -> 19 Wannier functions chosen:
  Nb s,p,d (9) + Fe s,d (6) + Sb s,p (4); frozen window 2.0-24.0 eV (CBM+6.5 eV); outer window 0-38 eV.
- Surprise: --test-only predicted hours of queue, but small/debug jobs started within seconds. The duplicate
  SCF (small + debug) both ran; the final tmp/ is from the debug run (identical input).

## 2. DFPT at Gamma (job 22919964, ph.out, dynmat.out)
- ph.x ldisp 1x1x1 (Gamma only, all that is needed for a q=Gamma kernel), epsil=.true., tr2_ph 1e-16, 3 min on 64 cores.
- eps_inf = 24.01 (isotropic); Z*: Nb +5.028, Fe -7.625, Sb +2.597 (ASR applied, sum = 0).
- Mode symmetry (ph.x): acoustic T2 (7.0 cm-1 raw, 0 with ASR), T2 at 214.5 cm-1, T2 at 275.5 cm-1 (all I+R).
- dynmat.x with asr='crystal': 0,0,0 | 214.54 x3 (6.4319 THz, IR 1.53) | 275.40 x3 (8.2564 THz, IR 30.05) cm-1.
- save/ built as EPW's pp.py would (dvscf_q1, dyn_q1, patterns.1.xml); nfs.dyn0 left in run/ because the
  modified EPW reads it for the irreducible-q order.

## 3. Wannierization (EPW internal, 19 WFs)
- Attempt 1 (job 22920019): disentanglement converged after ~900 iterations (Omega_I = 23.9 A^2, total spread
  53.5 A^2 at iteration 250 of wannierise), but the wannierise loop ran at 2.9 s/iteration with a 5000-iteration cap
  (would have taken ~4 h on 64 cores = 2 node-hours just for gauge polishing). Cancelled after 13 min.
- Attempt 2 (job 22920185): num_iter 1000, conv_tol 1e-7 (conv_window 3), precond, dis_conv_tol 1e-9. The
  disentangled subspace (which fixes the interpolated bands inside the frozen window) is the same.
- Attempt 2 (job 22920185) converged: 1000 wannierise iterations, total spread 28.29 A^2 (Omega_I 23.89), all 19 WFs
  between 0.62 and 2.44 A^2. EPW then aborted because QE 7.5's EPW expects the displacement patterns in
  dvscf_dir/prefix.phsave/patterns.N.xml (pp.py layout). Fixed save/ layout; job 22920374 reran the coarse step with
  wannierize=.false. (reads nfs.ukk) in 29 s and wrote epwdata.fmt/vmedata.fmt/dmedata.fmt/crystal.fmt/wigner.fmt.

## 4. Wannier interpolation quality (job 22920468, wannier/band_comparison.txt)
- EPW band_plot on the same 242 k-points as the pw.x bands run (G-X-W-K-G-L-U-W-L-K).
- Valence (bands 14-22, E<=VBM): RMS 1.29 meV, max 6.55 meV. Conduction CBM..CBM+6 eV: RMS 6.33 meV, max 55 meV
  (the max sits at the top of the window, bands 28-29 near 23.5 eV, where the frozen window ends at 24 eV and the
  WFs are the diffuse Nb s/p-like ones). Bands >= 29 are outside the frozen window and are not used in the metric.
- Decision: accept (a denser coarse mesh would cost ~1 node-hour of serial wannier90 time); the kernel's dominant
  features (3.4 eV) involve bands with few-meV errors.

## 5. Kernel runs (EPW lindabs kernel variant, q = Gamma, omega grid 0.01..6.00 eV step 0.01, degaussw 25 meV)
- EPW Gamma frequencies: 26.5995 meV (6.4317 THz) and 34.1159 meV (8.2492 THz) = DFPT T2 modes (214.5, 275.2 cm-1).
- 24^3 (job 22920469, 5m19s on 64 ranks): cost ~1.4 s per k-point per rank, dominated by the (i,j,l,omega) loops.
  Every mode peaks at 3.37 eV; the dominant channels are the off-diagonal xy/yz/zx ones, as required by Td symmetry
  (the only invariant third-rank-like coupling is of xyz type). Mode 8 (upper T2 triplet) has the largest invariant.
  Per-mode values inside a degenerate triplet depend on the basis chosen by the diagonalizer; the triplet sum is invariant.
- Plan: 48^3, 72^3, 96^3 on one full node each (small partition, started immediately); then decide on 120^3/128^3.
- 48^3 (job 22920568, 20 min), 72^3 (22920569, 71 min), 96^3 (22920570, 2h37m), each on one full node of `small`
  (started within minutes; `standard` test-only predicted a 2-day wait). Peak of mode 8: 29.09 / 28.94 / 29.08 / 29.01 A^2/eV
  at 3.37 / 3.35 / 3.35 / 3.35 eV for 24/48/72/96. 72->96 changes the peak by 0.2% and the spectrum by < 1.3% -> converged;
  a 120^3 run (~5.3 node-hours) was judged unnecessary. Delivered kernel = 96^3.
- Symmetry at 96^3: diagonal channels <= 0.55 vs off-diagonal maxima 7.7 A^2/eV (noise), tensor symmetric to 0.3%.
- Cleanup: deleted bands/tmp, run/tmp/_ph0, all wfc files (tmp and tmp_nscf); kept save/, *.fmt, nfs.epmatwp, nfs.ukk.

## 6. Final bookkeeping
- Total compute 4.47 node-hours (jobs.log, 14 jobs). Wall: 18:45 -> 22:27 UTC on 2026-10-16 (3.7 h).
- RESULT.json: peak 3.35 eV, I = 29.011 A^2/eV (mode 8, upper T2 triplet, 8.2492 THz in the kernel file; DFPT+ASR 8.2564 THz).
- Caveats recorded for the reader: (i) only diagram (c) is implemented in this build (no g^{s;alpha} term);
  (ii) per-mode values within a degenerate triplet are basis dependent, triplet sums are reported in REPORT.md;
  (iii) scalar-relativistic treatment of FR pseudopotentials, PBE gap 0.53 eV (no scissor applied).
