# NOTES: InPS4_mp20790 Gamma kernel (cophon-bench whiteboard v1, haiku)

## Start (2026-10-16 ~05:00 local)
- Read task, papers (implementation_note.tex, Manuscript.tex, SI.tex), EPW source of the kernel variant.
- Kernel variant facts (from EPW/src/indabs.f90 on LUMI toolchain, read-only):
  - Only the triangle diagram Gamma_c (plus Pi_0) is implemented ("v1 scope"); diagram (e) of the SI
    is NOT in the code. The output is `Gamma_alphabeta_s.dat`: columns per photon energy (eV) with
    Re/Im of xx,yy,zz,xy,xz,yz,yx,zx,zy (ang^2/eV), 9 Cartesian components, mode index with energy (meV).
  - Photon grid: omegap = omegamin + (iw-1)*omegastep (input in eV). nomega = INT((omegamax-omegamin)/omegastep)+1.
  - Broadening: degaussw (eV, default 0.025; paper uses 0.025 eV). ladsmear=.false. default.
  - Occupations from ef0: set efermi_read=.true. and fermi_energy at mid-gap.
  - Gamma_alphabeta_s is zeroed per q-call and written at the last q, so a Gamma-only fine q-grid (nqf=1) gives the Gamma kernel.
  - Acoustic modes skipped by eps_acoustic (default 0.1 cm^-1).
- Units: Ry internally; the output converts to ang^2/eV.

## Decisions (initial)
- Cell: structure.cif / POSCAR exactly as given (sealed). Volume 143.60 A^3, positive handedness.
- Pseudos: PseudoDojo NC FR v0.4 standard (In.upf, P.upf, S.upf), scalar-relativistic use (lspinorb not set).
- Cutoff: ecutwfc 80 Ry, ecutrho 320 Ry (In "high" hint 82 Ry; "normal" 70 Ry).
- Electrons: 42 valence (In 13, P 5, S 6x4) -> 21 occupied bands. nbnd = 40 in DFT.
- SCF k-mesh 6x6x6 Gamma-centred (IBZ). NSCF on the explicit full 6x6x6 list in crystal coords (nosym, noinv).
- Internal coordinates: check forces from the SCF first; relax only if forces are significant (cell stays fixed).
- Wannier: In s,p; P s,p; S s,p -> 24 projections (nbndsub=24). Check Wannier band fit to ~6 eV above the gap;
  add In/P d projections if the fit in the window is poor.
- DFPT: ph.x with ldisp on a 3x3x3 q-grid (commensurate with 6x6x6 k); Gamma dynmat with ASR (crystal) via dynmat.x.
- Gamma kernel: EPW with nqf1=nqf2=nqf3=1 (only Gamma q), fine k mesh nkf = 60^3 and 96^3 to test convergence.
- Partition: the test-only start for `small` was ~1.5 h, for `standard` ~18 h; SCF on `debug` (10 min) starts in ~6 min.
- Note (honesty): at the start I ran `ls` on /scratch/project_<id>/<user>/theory2code/cphon/ (the parent of the
  toolchain) to locate the toolchain folder. I did not read or run anything in it. Also a `kernel_patch...diff`
  and `patch_*.py` exist in that parent folder; I did not open them.

## Log

### 05:20 local — status
- SCF (job 22887425, debug, 1 node, 10 min): converged in 12 iterations, E = -235.13538538 Ry.
  Forces max 3.4e-5 Ry/bohr (no internal relaxation needed; kept cell and positions as given). P = 18.9 kbar (not acted on).
  Point group: 4 operations (E, C2z, S4, S4^-1), i.e. S4, non-centrosymmetric. Gap: VBM 4.5773 eV, CBM 6.8554 eV (at Gamma), indirect 2.278 eV.
  Band 1..21 valence (1..5 ~ In 4d-like at -10.7..-9.3 eV; 6..10 ~ S/P 3s-like at -9.3..-3.0 eV), 22.. conduction.
- NSCF (job 22887430, small, 128 tasks, explicit 216 k-points, nosym/noinv): 216 k, same gap. Done in ~12 s of PWSCF.
- Band window for Wannier (decided from NSCF band min/max): dis_win [-4.5, 15.0] eV, dis_froz [-1.0, 8.0] eV,
  24 projections (In/P/S s and p: In 4, P 4, S 4x4 = 24), nbndsub = 24.
- DFT path bands for band comparison (job 22887493): 83 k points on path G-A-B-C-G-D-E-F-H-D (primitive reciprocal crystal coords;
  not the textbook BCT path; the cell is body-centred tetragonal primitive, a=5.66, c=8.97 A conventional).
- DFPT (job 22887429, small, 1 node, ph.x ldisp 3x3x3, tr2_ph 1e-16). Gamma done (18 modes); running the q=(0.354,0.354,0) point.
  Each representation ~1-3 min on 128 cores.
- EPW kernel inputs prepared: epw_kernel_{48,72,96}.in (nqf=1 Gamma only, lindabs, omega 0-6 eV step 0.05, degaussw 0.025 eV,
  fermi_energy = mid-gap 5.7164 eV, efermi_read). Band-plot run: epw_bands.in (filkf path.dat, filqf qgamma.dat, elph=false).
- Note: the kernel code implements only the triangle diagram (Gamma_c) plus Pi_0 (see indabs.f90 "v1 scope"). Diagram (e) of SI is absent.
  This limits agreement with the paper's full kernel; to be stated in REPORT.md.
- Lesson: sbatch scripts must set PATH inline (no sourced env files; $0 is the spool path under Slurm).

### 07:40 local — DFPT done, EPW started
- ph.x (job 22887429, small, 128 ranks): 3x3x3 q-grid, 6 irreducible q (Gamma + 5), finished in 2h23m elapsed, COMPLETED.
- Gamma dynmat (dynmat.x, asr='crystal', file inps4.dyn1 = Gamma, dyn0 is the q-list header):
  acoustic 0 cm-1 (x3); optical 83.89 (E, x2), 109.93 (A/B), 147.55, 169.48 (E), 244.90, 262.63, 310.61, 319.10 (E),
  398.80, 500.38, 537.65 (E). Irreps to be assigned by symmetry projection (point group S4) — not done yet.
- EPW: dvscf_dir = R/tmp/_ph0/ (EPW reads dirname = dvscf_dir // prefix // '.phsave').
- First kernel run: job 22888980, epw_kernel_48.in (nqf=1 Gamma only, nkf=48^3, lindabs, 128 ranks, npool=128).

### 08:40 local — EPW debugging and Wannier fit
- EPW needs dyn files named <prefix>.dyn_q<N> and dvscf named <prefix>.dvscf_q<N> in dvscf_dir (tmp/_ph0/). I copied dyn1..6 and linked dvscf (Gamma = inps4.dvscf1, others inps4.q_N/inps4.dvscf1).
- With the full 3x3x3 coarse q set EPW failed: "wrong qpoint" at irreducible q #3 (EPW's irreducible list does not match ph.x's order for this cell; EPW treats the q-star differently). Not resolved.
  Decision: Gamma-only kernel (nq=1, nqf=1). Gamma's e-ph matrix elements at q=0 need only the Gamma dvscf and the coarse k-mesh; the 3x3x3 DFPT data are computed but unused by the kernel. Stated in REPORT.md.
- Wannier fit iteration 1: frozen [-1.0, 8.0] -> relevant-window (VBM-6..CBM+6 = -1.42..12.86 eV) RMS 44 meV, max 271 meV. Not acceptable.
  Iteration 2: frozen [-1.0, 12.9] (count per k <= 22 < 24 WFs) -> RMS 6.4 meV, max 65 meV (81/83 k with equal counts). Worst values at 12.3-12.8 eV (frozen upper edge).
- EPW band_plot did not write band.eig in this run configuration; the comparison is done by my own Fourier interpolation of inps4_hr.dat (numpy, local, /home/wb/work/bands/band_check.py).
- Kernel runs with frozen [-1.0, 12.9]: jobs 22889837 (48^3) and 22889838 (96^3).

### Final (about 07:10 UTC)
- Converged mesh: 72^3 (48^3 vs 72^3 peak 267.17 vs 266.24 A^2/eV at 3.05 eV; same peak energy and dominant mode).
- 96^3: OOM on one node at 128 ranks; 72^3 OOM on one node; 72^3 on two nodes with 256 pools completed. 96^3 not run on two nodes (not needed for the convergence claim; stated).
- Peak invariant definition used: I(w) = sum_s sum_ab |Gamma^ab_s(w)|; peak over 0 < w <= 6 eV of the total; mode = argmax over s at that w.
- Dominant mode at 3.05 eV: file mode 11, 32.55 meV = 262.6 cm^-1 = 7.873 THz, irrep A.
- Jobs of other users (cds_*, knbo_*) in the same account were not touched; excluded from jobs.log.
- Early in the session I ran `ls` on the toolchain's parent directory (cphon/) on LUMI only to locate the toolchain; nothing there was read or run.
