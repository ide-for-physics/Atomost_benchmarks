# NOTES: SnS2_mp1170 coherent-phonon kernel (sealed cell)

Running log of what was done and why. Times are wall-clock on this machine (2026-10-15 unless noted).

## 0. Starting state (found, not produced by this session)

- Local folder /home/wb/work contained only TASK.md, papers/, structure.cif, structure_POSCAR (plus the harness's launch.sh, transcript.jsonl, stderr.log). No NOTES/jobs.log existed.
- The remote root `.../bench_whiteboard_v1/SnS2_mp1170/` already held a previous attempt (dirs 01_relax, 02_scf, 03_ph, 06_epw, pseudo; ~6.6 GB; jobs 22874406, 22874459, 22874511, 22874562 on 16:00-16:40 cluster time). I did not create those files in this session.
- I did not reuse their results as production data. I moved the whole tree to `prior_attempt_archive/` (not deleted) and rebuilt the pipeline from scratch under `run/`. The archived tree is kept for audit only.
- What the archive shows (for the record): relax converged in 0 BFGS steps (|F|_max ~ 7e-5 Ry/bohr, so the sealed-cell positions are already relaxed); SCF/NSCF gap VBM 6.8295 eV, CBM 8.1629 eV (PBE, FR PseudoDojo used without SO); DFPT Gamma: E_g 206.4, A1g 311.7, A2u 340.5 cm^-1; EPW Wannierization with 10 WFs failed ("more states in the frozen window than target WFs"), so that attempt never produced a kernel.
- Budget accounting: the previous attempt's debug jobs total about 0.57 node-hours (listed in jobs.log, section "inherited").
- The ssh account is `<user>`, which is shared: `squeue`/`sacct` show jobs from other projects (CdS, InPS4, bench_b_*, ...) and SnS2 jobs named `sns2_epw1v2`, `sns2_epw3`, `sns2_epw3v2`, `sns2_epw4`, `sns2_epw1v3` (2026-10-14/15, 1-2 nodes, roughly 2-3 node-hours in total). I cannot attribute those to this root (they are not in its archive and their names do not match the archive), so they are NOT counted in jobs.log. I did not touch, cancel or read any job I do not own.

## 1. Sources and what the kernel variant computes

- Implementation note (papers/implementation_note.tex) and SI (papers/SI.tex, Sec. "First-principles calculation") define Gamma^{ab}_s(omega_s; omega,-omega) from diagrams (c) and (e). SI: electronic broadening 0.025 eV, the kernel is computed in EPW with the Gamma-point EPC matrix g^s and the velocity h^a from Wannier interpolation.
- Code read in the toolchain (EPW/src/indabs.f90, subroutine that writes `Gamma_alphabeta_s.dat`):
  - The kernel loop implements the triangle (diagram c) term with Gaussian-broadened delta functions (degaussw), with the output in Ang^2/eV, columns per photon energy: xx, yy, zz, xy, xz, yz, yx, zx, zy, each as (Re, Im). Modes 4..nmodes are written (acoustic modes 1-3 skipped).
  - The diagram (e) term and the second-order Y/M terms are NOT in this v1 kernel (the file header says "Gamma_c triangle + Pi_0, v1 scope; Gamma_e out of scope"). The grader compares against the same variant, so I use the output as produced and report this limitation.
  - The kernel is gated by `lindabs = .true.` (use_wannier.f90, branch `lindabs .AND. .NOT. scattering`); photon grid from `omegamin/omegamax/omegastep` (eV) with `nomega = INT((omegamax-omegamin)/omegastep)+1`.
  - It is accumulated per q-point and written at `iq == lastq`; with a 1x1x1 fine q-grid this is the Gamma point.
- Output of the kernel for the "rotational invariant": the paper does not define one (grep of Manuscript/SI/implementation note finds no "invariant"). My definition, used for RESULT.json: for each mode s, I_s(omega) = sum over Cartesian (a,b) of |Gamma^{ab}_s(omega)| (the complex magnitude of each of the 9 tensor components, summed). The peak is max over omega in [0,6] eV of sum_s I_s, and the mode is the mode with the largest I_s at that photon energy. This is recorded in REPORT.md as a definition, not as a paper result.

## 2. Electronic-structure choices

- Structure: sealed cell from structure.cif (identical to structure_POSCAR; checked both give a=3.639, c=5.868 Å, gamma=120 deg, Sn (0,0,0), S (1/3,2/3,0.254186), S (2/3,1/3,0.745814)). No vc-relax. Internal coordinates were not changed (relax from the archive confirms they are at equilibrium for this cell).
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (fully relativistic UPF) used in scalar-relativistic mode (no SO), as the task allows. md5 of Sn.upf and S.upf match the originals in /home/wb/pseudos.
- Cutoff: ecutwfc = 80 Ry, ecutrho = 320 Ry. PseudoDojo hints: Sn normal 72 Ry (high 84), S normal 52 Ry (high 64). 80 Ry is above normal for both.
- SCF: 12x12x6 Gamma-centred, occupations fixed, conv_thr 1e-12, diago_thr_init 5e-6 (the Davidson quirk in the task).
- DFPT: ph.x at Gamma (ldisp, nq=1), epsil=.true., tr2_ph=1e-16; dynmat.x with asr='crystal'.
- NSCF: full 12x12x6 list (864 points, explicit crystal list in [0,1), nosym, noinv), nbnd = 30 so the conduction manifold up to ~6 eV is available for the Wannier fit.
- Path for band comparison: G-M-K-G-A-L-H-A | L-M | K-H (hexagonal, 113 points, same list used for DFT and Wannier bands).


## 3. Wannier model (decisions and evidence)

- Wannier set: `proj = Sn:s;p;d`, `S:s;p` -> 17 WFs (nbndsub = 17), `exclude_bands = 1-5` (Sn 4d semicore). DFT bands 6-22 are the Wannier manifold.
- Why 17: the archived attempt used 10 WFs and its frozen window held more states than WFs (wannier90: "More states in the frozen window than target WFs"). I did not run a 12-WF set. I went to 17 WFs (Sn s,p,d + S s,p), which gives room for the frozen window (up to 13 states at some k below 14.6 eV) plus the outer-window states above it.
- Windows (attempts recorded in jobs.log): outer -8 .. 22.5 eV (the 18.5 eV outer window gave only 16 states at one k-point, wannier90 error), inner (frozen) -8 .. 14.6 eV (14.6 eV, not 11.5 eV: with 11.5 eV the conduction bands at 11.8-14.5 eV were off by 64-115 meV RMS).
- Minimisation: dis_num_iter 400, num_iter 400 (wannier90 needed ~1.2 s/iteration here; the 2000-iteration setting could not finish in the 20-min debug limit and was cancelled). The final spread is 45.0 Ang^2 (not fully converged); the band interpolation error is what matters for the kernel, and it is small (below).
- Attempt-5 quality (wannier/wannier_vs_dft_summary.txt; 113 k-points along G-M-K-G-A-L-H-A|L-M|K-H):
  - valence (DFT bands 6-13): RMS 0.94 meV, max 4.96 meV;
  - conduction up to CBM+6 eV (14.18 eV): RMS 1.54 meV, max 11.8 meV.
  - Bands W13-W17 (DFT 18-22, above 13.2 eV) are NOT reproduced (RMS 0.2-0.7 eV). Argument that this does not affect the kernel at 0-6 eV: in indabs.f90 every term is gated by a window on the transition energy near the photon energy omega (|eps - omega| <= 6 eta), so a state contributes only if it is within about omega (<= 6 eV) of a valence state, i.e. below ~12.8 eV. The mis-described bands start at 13.2 eV, so they never enter a resonant term for omega <= 6 eV.
- Gap: DFT VBM 6.831 eV, CBM 8.176 eV (path), gap 1.345 eV (indirect; NSCF grid VBM 6.8295, CBM 8.1628). The EPW Fermi level for the kernel is set to midgap 7.4962 eV (efermi_read), so f_mn is the insulating occupation.

## 4. Kernel run settings

- EPW kernel input (inputs/epw/epw_kernel_k<N>.in): lindabs = .true., omegamin 0.1 eV, omegamax 6.02 eV, omegastep 0.02 eV -> 297 photon energies (0.10-6.00 eV on the grid; the last point 6.02 eV is one step beyond 6 eV and is kept, not trimmed), degaussw 0.025 eV (the SI broadening), nkf1=nkf2=nkf3=N, nqf=1 (Gamma only), lpolar = .false. (Gamma-only, no polar correction at q=0), asr_typ = 'crystal'.
- The photon grid starts at 0.1 eV, not 0: the kernel carries 1/omega^2 (`ci*pi/(omegap)**2` in indabs.f90), which diverges at omega = 0 and would write Inf to the file. Below 0.1 eV the kernel is not defined in this code.
- Gamma-only q-grid (nq = nqf = 1) so only the Gamma phonons appear; modes 1-3 (acoustic, skipped by the code) and modes 4-9 (Eu, Eg, A1g, A2u) are written.
- Fine-mesh convergence set: 48^3 (done, 64 tasks, 13.5 min), 72^3 and 96^3 (queued, one allocation, 128 tasks each). The mesh is N x N x N as in the task's example format; the Wannier coarse grid is 12x12x6.

## 5. Kernel invariant and checks

- Invariant (defined here, see section 1): R(omega) = sum_s sum_ab |Gamma^{ab}_s(omega)|, peak = argmax over 0..6 eV; mode = argmax_s of the per-mode term at the peak. The Frobenius variant (sqrt of sum |Gamma|^2 per mode) is reported only as a cross-check.
- Symmetry check (inversion): SnS2 (P-3m1) is centrosymmetric, so IR-only (u) modes must give zero second-order kernel. Eu (modes 4-5) gives max |sum|Gamma|| = 0.13-0.20 Ang^2/eV against 34 (Eg) and 80 (A1g) Ang^2/eV: about 0.2 % of the Raman modes. This residual is attributed to the finite k-mesh/IBZ symmetrisation and is reported, not removed.
- A2u (modes 1 and 9) and acoustic modes: A2u mode 9 is 0.17 Ang^2/eV max (u-mode, same argument). Acoustic modes 1-3 are not written by the code.

## 6. Status (updated during the run)

- Done: DFT/SCF, DFPT at Gamma with ASR, NSCF 864 points, bands path, Wannierization (17 WFs), band comparison, kernel on 48^3 (kernel/Gamma_alphabeta_s_48x48x48.dat, raw copy in kernel/raw/).
- 72^3 then 96^3 ran in one allocation (job 22879158, small, 128 tasks each). It started at once (19:39 local), not at the 21:32 estimate, and took 73 min.
- Remaining: final kernel file at the converged mesh, RESULT.json (analysis/make_result.py), REPORT.md, jobs.log totals, DONE.

## 7. Final

- Converged mesh: 96x96x96 (72^3 and 48^3 agree on the peak within 0.04 eV; R at peak changes 1.5% from 72^3 to 96^3).
- Adopted kernel: kernel/Gamma_alphabeta_s.dat (= kernel/Gamma_alphabeta_s_96x96x96.dat). RESULT.json is generated by analysis/make_result.py from that file and jobs.log.
- Peak: 5.44 eV, R = 141.29 Ang^2/eV, dominant mode A_1g at 9.345 THz.
- Compute: 2.453 node-hours (jobs.log). Wall-clock about 2.4 h to DONE.
