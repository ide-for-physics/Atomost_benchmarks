# NOTES: Bi2O2Se light-induced coherent-phonon kernel (cophon-bench v1, whiteboard, haiku)

## Start
- 2026-10-16 ~06:40 local. Read papers/: Manuscript.tex (Gamma^{ab}_s definition, Eq. Gamma_2nd_final),
  SI.tex (diagram c and e, Methods: eta=0.025 eV, 90 Ry), implementation_note.tex (code route: wan2bloch, indabs).
- Toolchain: /scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75 (QE 7.5 + kernel EPW).
  Read EPW/src/indabs.f90 (kernel assembly + output) and readin.f90 (units, defaults).

## Decisions so far (and why)
- Cell: sealed POSCAR cell used exactly (ibrav=0). Positions may be relaxed at fixed cell (bfgs), done first.
- Pseudos: PseudoDojo FR ONCV v0.4 standard (Bi.upf, Se.upf, O.upf), scalar-relativistic use (no lspinorb).
- Cutoff 90 Ry / 360 Ry (paper SI value). Insulator: occupations='fixed', 58 electrons -> 29 occupied bands.
- SCF / DFPT / EPW coarse k-mesh: 8x8x8 (same grid for ph.x and the explicit full-grid NSCF list).
- degaussw = 0.025 eV (paper SI: electronic broadening 0.025 eV).
- Photon grid: omegamin > 0 because the code's prefactor is ci*pi/omega^2 (singular at 0). Plan: 0.01..6.00 eV.
- EPW kernel output file: Gamma_alphabeta_s.dat (eV, A^2/eV, 9 complex channels per mode).
- Code scope: indabs.f90 assembles ONLY the triangle diagram (c) (Gamma_c with epf17, vmef); the comment says
  Gamma_e / epvf17 is out of scope in this variant. The SI says (c) and (e) are both used. Report this as a limit;
  do not patch the authors' code.
- Rotational invariant (paper does not define it explicitly; grep of Manuscript/SI/implementation note found none):
  I_s(omega) = sum_{ab} |Gamma^{ab}_s(omega)| over the 9 Cartesian channels, per mode. Peak = max over (s, omega).
  The Frobenius-norm alternative is reported in REPORT.md as a cross-check.
- Phonon irreps: to be derived from the symmetry operations (pw.x output) projected onto the Gamma eigenvectors.

## Scheduling
- small partition: test-only start estimate ~08:13 local for a 16-64 task job (queue dominated). Standard has ~380 pending.
- Small jobs are charged by processors used (32 tasks -> 64 processors); node-hours = processors/128 x hours.

## Calculation chain (what was run, in order)
1. Relax internal coords at sealed cell (bfgs, 8x8x8, 90/360 Ry): converged in 1 BFGS step, tiny displacement
   (Bi x 0.353125 -> 0.3531302). Relaxed positions used everywhere after.
2. SCF 8x8x8 (conv 1e-11): gap 0.33 eV (VBM 10.669, CBM 10.998 eV absolute), 58 e, 29 occupied bands.
3. NSCF on explicit full 8x8x8 list (512 pts), nbnd=44 (EPW needs the full list for Wannierization).
4. DFPT at Gamma (ph.x, tr2_ph 1e-13) run from a FRESH SCF (8x8x8, IBZ 59 k) in phrun/. ph.x run
   from the NSCF data-file was ~16x too slow (it used the 512-point list) and was cancelled.
   pp.py needed symlinks (bi2o2se.save, _ph0) in the working dir; gathered save/ manually.
5. Raw Gamma frequencies (cm^-1, ph.x, before ASR): acoustic -31.4, 9.4, 9.4; optical 45.3 61.7 61.7 90.6 90.6
   156.2 251.8 251.8 340.8 367.2 412.9 412.9. Raw ASR violation is large (dynmat simple ASR: -34.7 cm^-1 pair).
6. ASR: EPW default asr_typ='simple' applies to the direct dyn route and leaves a -34.7 cm^-1 pair, which EPW
   zeroes and the kernel then skips. Consistent route: q2r.x zasr='crystal' -> ifc.q2r in save/, EPW lifc=.true.,
   asr_typ='crystal'. All kernel runs with crystal ASR use this. Optical frequencies (crystal ASR) are
   51.1, 60.1, 60.1, 61.7, 61.7, 156.2, 259.2, 259.2, 340.8, 372.0, 412.9, 412.9 cm^-1 (12 optical modes).
7. Wannier: EPW internal (Wannier90 library), 8x8x8 coarse grid, degaussw 0.025 eV, fsthick 9 eV.

## Wannier-interpolation check (bandcheck/compare_variant.py; DFT bands along G-A-B-G-C, 49 pts)
Each variant: RMS/max deviation of Wannier band vs matched DFT band (meV), valence (VB, all k below VBM)
and conduction bands up to CBM+6 eV.
- Original (18 WF, froz VBM-7..VBM+6.5, outer VBM-10.7..VBM+10): valence rms 28.9 meV (max 332), CB rms 39 (max 318).
- wv2 (18 WF, froz VBM-6..VBM+5): valence rms 1.3 (max 19), CB 30-33 rms <=2.5 meV, CB 34-36 bad (rms 33/27/988 meV).
- wv3/wv4 (20 WF, outer -2..22 eV): fail (rms 200-700 meV) — wider outer window hurts. Rejected.
- wv5 (18 WF, froz VBM-6..VBM+5.5, outer VBM-10.7..VBM+10): valence rms 1.3 (max 19); CB 30-33 rms 0.9-2.5 meV
  (max 10.5); band 34 rms 33 (max 232), band 35 rms 12.6 (max 86); band 36 bad (rms 987).
- wv6 (18 WF, froz VBM-6..VBM+6): valence worse at deep band 20 (rms 49), CB 30-35 rms 2-13.
- ADOPTED: wv5. Reason: best valence and CB-to-4.4 eV agreement, which is where the kernel peak sits (~3.8 eV).
  LIMIT: Wannier interpolation of CB bands above ~4.5 eV (bands 34-36) is off by 30-300 meV; kernel values above
  ~4.5 eV carry that error. Reported, not fixed.

## Final status (2026-10-16, ~12.3 h wall, 8.83 node-h)
- Adopted: wv5 Wannier set (18 WF, frozen VBM-6..VBM+5.5 eV, outer VBM-11..VBM+10), crystal ASR via q2r.x + EPW lifc,
  kernel diagram (c) only (code scope), degaussw 0.025 eV, fsthick 9 eV, omega grid 0.01-6.00 eV step 0.01.
- Peak (rotational invariant sum|Gamma| over 9 channels): 40.11 A^2/eV at 3.80 eV, mode 9 (156.2 cm-1, A1g). Frobenius alt: same mode/energy.
- Mesh: 32^3 (mode 12 peak 47.6 @2.45 eV — not converged), 48^3 (41.96 @3.79), 64^3 (40.11 @3.80). 80^3 queued on Priority
  for >1.5 h and cancelled (not run). Magnitude 48->64 changes -4.4%; convergence stated as not fully established.
- Wannier: valence and conduction up to ~4.4 eV above VBM within 2.5 meV RMS; bands above ~4.5 eV (W16-W18) fail
  (RMS 33 / 13 / 987 meV). Stated in REPORT as a failed requirement.
- Kernel scope: diagram (c) only (indabs.f90 header: Gamma_e out of scope in this variant). Not the full paper kernel.
- Not done: 80^3 mesh; eigenvector-projected irreps for ASR-shifted modes (labels tentative); diagram (e).
- Mistake noted: one command listed a directory outside the root (names only). No content read or copied from outside root.
- Files: RESULT.json, REPORT.md, kernel/Gamma_alphabeta_s.dat (= 64^3), kernel/Gamma_alphabeta_s_{32,48,64}.dat,
  kernel/superseded/ (old Wannier and wv5 duplicates), inputs/used/ (exact inputs), kernel_runs/ (EPW outputs),
  evidence/ (SCF/NSCF/ph/ASR outputs), bandcheck/ (Wannier-vs-DFT data and comparison scripts), jobs.log, DONE.
