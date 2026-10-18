# NOTES — KNbO3_mp7375 light-induced coherent-phonon kernel (cophon-bench v1)

## Setup (2026-10-16)
- Cell: structure.cif == structure_POSCAR, sealed (no vc-relax). Simple-cubic-like primitive cell, a = 4.005 A, V = 64.24 A^3,
  5 atoms (K, Nb, O x3), 40 valence electrons (K 9, Nb 13, O 6 each) -> 20 occupied bands.
- Pseudos: PseudoDojo nc-fr-04 pbe standard (K.upf, Nb.upf, O.upf, fully relativistic UPF used scalar-relativistically, no SOC).
  Hints (djrepo): normal cutoff K 74 Ry, Nb 82 Ry, O 84 Ry; high O 96, Nb 98 Ry. Decision: ecutwfc = 90 Ry (ecutrho = 360 Ry).
- Toolchain (LUMI): qe-phnlo-75 at /scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75 (bin/ has pw.x ph.x wannier90.x
  pw2wannier90.x epw.x dynmat.x). Modules: LUMI partition/C, PrgEnv-gnu, cray-fftw.

## What the kernel variant actually computes (read from EPW/src/indabs.f90 in the toolchain, not from the paper)
- Writes Gamma_alphabeta_s.dat in the EPW working dir (from indabs_main, only on the last q). Header: photon energy (eV) then
  Re/Im pairs for xx,yy,zz,xy,xz,yz,yx,zx,zy in ang^2/eV; block per mode for imode = 4..nmodes (acoustic modes 1-3 skipped).
- Implemented: triangle diagram Gamma_c (+ Pi_0 written separately to Pi_0.dat). Gamma_e (phonon-Stark / the optically perturbed EPC
  term diagram (e) of SI Eq. diagram_e) is marked "out of scope in v1" in the source (input flag lgammae is declared but unused).
  => The kernel is Gamma_c only. This is a limitation of the code, reported as such.
- Photon grid: omegap = omegamin + (iw-1)*omegastep, nomega = INT((omegamax-omegamin)/omegastep)+1. Kernel divides by omega^2, so
  omegamin must be > 0. Chosen: omegamin 0.05 eV, step 0.05 eV, omegamax 6.0 eV.
- Broadening: degaussw = 0.025 eV (SI: electronic broadening 0.025 eV). ladsmear = .false.
- Acoustic cut: eps_acoustic default 0.1 cm^-1.
- Input flags needed: lindabs = .true. (and vme = 'wannier', default). lgammae left .false.
- Note file itself (implementation_note.pdf) says the diagnostic spectra are under validation and that a vvmewan2bloch branch
  inconsistency (ci factors) exists; this is the code the task asks us to use, so we use it as shipped and report the caveat.

## Invariant definition (decision)
- The task asks for "per-mode magnitudes summed over Cartesian channels". Adopted: I_s(w) = sum_{ab} |Gamma^{ab}_s(w)| over the
  nine Cartesian channels (|Re + i Im| per channel), total I(w) = sum_s I_s(w). peak = max over w in [0,6] eV of I(w);
  mode_thz = dominant s at that w (argmax of I_s). Documented again in REPORT.md.

## Plan
1. pw.x SCF, 6x6x6 unshifted k, fixed occupations, nbnd 30, conv_thr 1e-12; check forces (positions given as relaxed).
2. ph.x Gamma-only DFPT with fildvscf (for EPW), tr2_ph 1e-14; dynmat.x with ASR for Gamma frequencies.
3. pw.x NSCF on explicit 6x6x6 full list (216 pts) for pw2wannier90 + EPW coarse grid.
4. wannier90 (O p + Nb d, 14 WF) with disentanglement; band comparison DFT vs Wannier along high-symmetry path.
5. epw.x kernel runs at fine meshes (at least two), e.g. 24^3 and 48^3, then 72^3/96^3 if affordable; pick converged mesh.
6. Budget: 20 node-hours total. Use the `small` partition (shared nodes) for this 5-atom cell (cheap).

## Log (chronological)
- SCF pw.x (job 22886060, small, 6x6x6 unshifted, ecut 90 Ry, nbnd 30, fixed occ.): converged in 14 iterations, E = -284.34960483 Ry.
  VBM 8.4106 eV, CBM 10.6173 eV on the 6x6x6 grid (gap 2.21 eV). Forces <= 1.6e-4 Ry/bohr, total force 1.9e-4:
  the supplied internal coordinates are already relaxed, so no internal relaxation was needed. Point group 6 ops, no inversion
  (polar, the second-order kernel is allowed by symmetry).
- DFPT at Gamma (ph.x, job 22886067, epsil=.true., tr2_ph 1e-14): optical frequencies 183.3(x2), 186.5, 202.9(x2), 239.4, 248.0,
  275.5(x2), 518.1(x2), 570.7 cm^-1; acoustic -7.6, -5.8, -5.8 cm^-1 before ASR (to be fixed with dynmat.x asr='crystal').
- NSCF on explicit 216-point 6x6x6 full list (job 22886068): same VBM/CBM. Bands at Gamma: 12-20 O 2p (6.24..7.52 eV),
  21-23 Nb t2g (10.62..10.84), 24-25 Nb eg (14.23), 26 15.19, 27-28 16.54, 29-30 19.48.
- Wannier model v1 (14 WF: Nb d + O p): windows 2..17 failed (energy window had < 14 states at some k, band 25 reaches 18.3 eV).
  After widening to 2..20 eV the O 2p fit is good (RMS 1.0 meV, max 9.7 meV, 12-20), but Nb eg bands (24-25) deviate by up to
  1.8 eV and bands 21-23 by 20-100 meV RMS within CBM+6 eV. Bands 26-28 (15-16.5 eV) lie inside the CBM+6 eV window and are not in
  the model at all.
- Wannier model v2 (18 WF: Nb d + Nb sp + O p, dis_win 2..20, dis_froz 3..16.8): to cover the CBM+6 eV window (16.6 eV).
  This is the adopted model (nbndsub = 18 in EPW). Comparison to be redone with it.
- Kernel windows: photon grid omegamin 0.05 eV, step 0.05 eV, to 6.0 eV (nomega 120), degaussw 0.025 eV.

## Kernel runs and final decisions
- Wannier model adopted: 14 WF (Nb d + O p), outer 2–20 eV, frozen 3–11 eV. The 18-WF variants (Nb s/p added) were tried and rejected:
  they degrade valence (RMS 11.8 meV) for a conduction gain (12.6 meV). Band comparison in wannier/.
- EPW inputs: epw_template.in (lindabs, omegamin 0.05, omegamax 6.0, omegastep 0.05, degaussw 0.025, nbndsub 14, wannierize with
  proj Nb:d, O:p, dis windows as above, nk 6x6x6, nq 1x1x1, nkf = 12/24/48/72/96, dvscf_dir '../../ph/tmp/_ph0/').
- Pipeline workarounds needed (documented for reproducibility): EPW reads the NSCF wavefunctions (symlink to the NSCF save dir,
  not copies); EPW needs dyn file named knbo3.dyn_q1 and dvscf named knbo3.dvscf_q1 in dvscf_dir (copies of ph.x outputs);
  pseudo symlink epw/pseudo -> ../pseudo; dvscf_dir relative to the EPW run dir. nbndskip is not a valid EPW keyword.
- Memory: 72³ and 96³ ran out of memory at 32/64 ranks; 72³ ran on 128 ranks (one node), 96³ on 256 ranks (two nodes).
- Kernel mesh convergence: 12³ 3.90 eV/282.3; 24³ 3.55/201.4; 48³ 3.60/180.1; 72³ 3.30/179.6; 96³ 3.30/179.5 Å²/eV.
  Converged mesh: 96x96x96 (magnitude converged to 0.06% between 72³ and 96³).
- Fine-grid Fermi level reported by EPW: 9.12 eV (in the gap; VBM 8.41, CBM 10.62).
- Result summary and caveats are in REPORT.md; numbers in RESULT.json come from kernel/Gamma_alphabeta_s.dat (kernel_peak.py).
