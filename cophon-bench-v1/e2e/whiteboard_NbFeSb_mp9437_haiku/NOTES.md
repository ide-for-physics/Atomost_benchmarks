# NOTES: NbFeSb_mp9437 coherent-phonon kernel (running log)

## Setup
- Structure: sealed cell from structure.cif = structure_POSCAR, fcc primitive, a_prim = 4.16753 A (|a_i| = 4.1675 A, 60 deg). Half-Heusler, Nb 0,0,0; Fe 1/4,1/4,1/4; Sb 1/2,1/2,1/2 (crystal). No vc-relax. Sites are symmetry-fixed (Td), so no internal relaxation expected; forces checked in SCF.
- Remote root: /scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/NbFeSb_mp9437/ (pp/, run/).
- Toolchain: qe-phnlo-75 (QE 7.5 + kernel-variant EPW). Modules: `LUMI partition/C PrgEnv-gnu cray-fftw`.
- Kernel output: EPW writes `Gamma_alphabeta_s.dat` (indabs.f90): per mode, columns = photon energy (eV), then Re/Im of xx, yy, zz, xy, xz, yz, yx, zx, zy (Ang^2/eV). Modes 4..nmodes (acoustic 1-3 skipped).
- Implementation note: EPW input flags `lindabs`, `degaussw` (dephasing width, paper uses 0.025 eV), `omegamin/omegamax/omegastep` (eV), `ladsmear` (off by default). Note section IV lists known open issues (q=0 only; eig_read path unsupported for vvmef; degeneracy blocks disabled; vvmewan2bloch branch inconsistency with ci factors). These must be recorded in REPORT.md as caveats.

## Shared-account caution
- The LUMI login account is `<user>`. `squeue` shows NbFeSb_mp9437 jobs (2208xxxx, e2eH/e2eF kernel) and other benchmarks' jobs under this account that I did not submit. I do not cancel, modify or use them.

## Decisions
- ecutwfc 90 Ry (PseudoDojo hints: Nb normal 82, Fe normal 90, Sb normal 80 Ry; SI uses 90 Ry).
- Pseudos: PseudoDojo FR v0.4 standard NC (has_so=T). Used with lspinorb off (scalar-relativistic use, allowed by the task). Valence: Nb 13, Fe 16, Sb 15 = 44 e -> 22 occupied bands.
- Insulating: occupations='fixed'.
- SCF mesh 8x8x8 Gamma-centred. conv_thr 1e-10, diago_thr_init 5e-6 (build quirk).
- Queue choice: `debug` for the SCF (expected < 10 min, starts immediately). Small partition estimated 3 h wait at submission; standard about 1 day.

## Log
- 1st SCF attempt failed in readpp: pseudo_dir './pp' is relative to run/ and pp is in ../pp. Fixed to '../pp', resubmitted (job 22877758).

## Calculations so far (all LUMI, partition debug unless noted; charge = AllocCPUS/128 x elapsed)
- SCF 8x8x8, 90 Ry, fixed occupations: VBM 16.9722 eV, CBM 17.5050 eV (PBE gap 0.533 eV). Forces 0 (symmetry), P = 62.5 kbar (cell sealed, not relaxed).
- DFPT at Gamma (ph.x, epsil=.true., tr2_ph 1e-14): acoustic residual 13.2 cm-1 before ASR; after dynmat.x asr='crystal' acoustic = 0. Optical: 214.9 cm-1 (IR intensity 1.6), 274.9 cm-1 (IR intensity 30.0). Td site symmetry: each atom displaces as T2, so all three triplets are T2 in ph.x/dynmat labelling. The 274.9 cm-1 triplet is the strongly polar one. Z*(Nb)=5.03, Z*(Fe)=-7.63 (ASR applied).
- NSCF 6x6x6 full grid (nosym, noinv, explicit 216 k list) and path NSCF (131 pts): VBM/CBM reproduced.
- Wannier: wannier90 via EPW (wannierize). First attempt with 16 WFs (s,d / s,d / s,p) and disentangle window 4.5-26 eV gave valence RMS 45 meV, max 226 meV, conduction RMS 312 meV (max 1.9 eV) - rejected. Cause: too few WFs for bands 23-29. 22 WFs (Nb s,p,d; Fe s,p,d; Sb s,p), outer window 4.5-33 eV, frozen 4.5-17 eV, 6x6x6 coarse grid: valence (bands 14-22) RMS 14.5 meV, max 68 meV; CBM..CBM+6 eV RMS 12.4 meV, max 68 meV.
- Band-structure check done in python (check_bands.py, wannier90 hr interpolation vs DFT XML on the 131-pt path). EPW band_plot path did not write output in this build (restart mode), so the check uses nbfesb_hr.dat.
- EPW input notes learned: bands_skipped='exclude_bands = 1:13' (no nbndskip key); dvscf_dir must contain prefix.phsave + prefix.dyn_q1 + prefix.dvscf_q1 (copied from _ph0 as in toolchain diamond/phonons/pp.py); nqf=1 needed; band_plot forbids nkf/nqf; epbread incompatible with epwread.

## Wannier band check (final)
- 8x8x8 coarse grid, 22 WFs (Nb s,p,d; Fe s,p,d; Sb s,p), outer window 4.5-33 eV, frozen 4.5-17 eV.
- Valence bands 14-22 (all 131 path k): RMS 6.2 meV, max 40 meV. Conduction states CBM..CBM+6 eV: RMS 8.2 meV, max 66 meV (max at top edge ~23.7 eV).
- Data: logs/bands/band_compare_path.csv, logs/bands/band_compare_summary.txt; script inputs/check_bands.py.
- Earlier 6x6x6 attempt with 22 WFs: valence RMS 14.5 meV, max 68 meV (superseded).

## Kernel (EPW indabs, lindabs=.true., degaussw=0.025 eV, temps=300 K, omega 0-6 eV step 0.01 eV, fermi_energy=17.2377 eV mid-gap)
- Mesh 12x12x12 (debug, 32 ranks): peak 27.21 A^2/eV at 3.37 eV, mode 274.8 cm-1.
- Mesh 48x48x48 (small, 128 ranks, 30 min): peak 19.04 A^2/eV at 3.36 eV, mode 274.8 cm-1. 12->48 changes the peak by 30%, so mesh convergence still open.
- Mesh 72x72x72 was queued, then cancelled to protect node-hour budget (estimated ~3.4 node-h).
- Mesh 96x96x96: first attempt OOM on 1 node (128 ranks, memory per rank ~2 GB+ scales with the fine-grid arrays; ReqMem default 112 GB/node). Retried with 2 nodes x 64 ranks: still OOM at 112 GB/node default; retried with --mem=240G/node: interconnect launch failure on the first try; resubmitted.
- Invariant used: I_s(w) = sum over the 9 Cartesian channels of |Gamma^ab_s(w)| (task definition; the papers do not give an explicit formula). Frobenius sqrt(sum |G|^2) reported as a cross-check.
- Known issue in the output: w=0 row is NaN for every mode (1/(hbar w)^2 prefactor). Excluded from the peak search. Left as written by the code.
- Triplet caveat: modes 7,8,9 (T2 triplet) give slightly different per-mode I (27.2/24.2/26.4 at 12 mesh) because EPW's degenerate eigenvector basis is arbitrary. The peak is reported for the per-mode definition; the triplet sum is also in REPORT.
- Budget: node-hours charged as cores/128 x elapsed (Slurm AllocCPUS shows 2x because of hardware threads; both are recorded in jobs.log).

## Final state (DONE)
- Adopted kernel: 96x96x96 (kernel/Gamma_alphabeta_s.dat). Peak I = 19.010 A^2/eV at 3.36 eV, mode 274.8 cm-1 (T2, polar). 48, 72, 96 peaks agree to 0.15%; 12 is not converged.
- Node-hours 9.42 (jobs.log). Budget 20. Wall ~12.2 h.
- Decisions (see REPORT.md): invariant = sum over 9 Cartesian channels of |G|; Frobenius reported as check; NaN row at w=0 kept; eig_read=.FALSE. branch used (note section IV.I inconsistency unresolved); 22 WFs with 8x8x8 coarse grid.
- Not done / limits: EPW band_plot output not produced in this build (band check uses wannier90 H(R) interpolation); 72-mesh and 96-mesh used 1 node; no relaxation (sealed cell, zero forces); pseudopotentials are FR PseudoDojo used scalar-relativistically (allowed).
