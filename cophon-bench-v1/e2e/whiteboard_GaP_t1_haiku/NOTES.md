# NOTES: GaP_t1 coherent-phonon generation kernel (running log)

## Setup decisions (2026-10-15)
- Cell: sealed `structure.cif` / `structure_POSCAR` (fcc primitive, a_conv = 5.4472 A, |a_i| = 3.8517 A). No vc-relax.
  GaP zincblende has no free internal coordinate (Ga 1/4,1/4,1/4 and P 0,0,0 fixed by symmetry), so internal relaxation is a no-op; check forces in scf.out.
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard, fully relativistic UPF used in scalar-relativistic mode (lspinorb = .false.), as allowed by the task.
- Cutoff: 80 Ry wfc / 320 Ry rho (PseudoDojo "normal" hint for Ga = 80 Ry; P hint = 44 Ry).
- Valence: Ga 13 e (3d included), P 5 e -> 18 e -> 9 occupied bands (5 Ga-3d bands + 4 bonding bands).
- SCF k: 8x8x8 unshifted; DFPT: ph.x ldisp 4x4x4 q (includes Gamma), epsil = .true. for Born charges / LO-TO; tr2_ph = 1e-14 (paper's 1e-16 is below ph.x practical floor).
- Queue at 2026-10-15 12:30 UTC+: small starts within ~45 min, standard ~21 h away -> everything on `small`.
- Kernel code: EPW/src/indabs.f90 (`indabs_main`) writes `Gamma_alphabeta_s.dat` (complex, 9 Cartesian channels per mode, columns Re/Im) and `Pi_0.dat`. The source header says "v1 scope": Gamma_c triangle + Pi_0 only; Gamma_e and Pi_kernel are out of scope. This is a limitation of the deliverable and must be stated in REPORT.md.
- Invariant for peak: the manuscript/SI/implementation note do not define a rotational invariant explicitly. Working definition: I_s(omega) = sqrt( sum_{ab} |Gamma^{ab}_s(omega)|^2 ) (Frobenius norm, rotationally invariant), reported per mode and summed over modes for the peak. To be revisited if the paper defines it.
- Known open issues from implementation_note.tex (to be cited in REPORT): vvmewan2bloch branch inconsistency (missing ci factors in eig_read=.FALSE. branch); eig_read path does not support vvmef; epsilon/kernel gauge issues. Read in REPORT as limitations.

## Log
- Job 22864746: pw.x SCF (8x8x8, 80 Ry), small partition, 32 tasks, submitted.
- Note: the same LUMI account has other jobs queued (e.g. 22863372/22863382 `GaP_t1_e2eF/H_epw1`, CdS, InPS4, NbFeSb) that were NOT submitted by this run. Not touched, not used.
- Remote root is shared with another run (directories 01_scf, 02_ph, 03_wan, 04_epw, job1/job2 scripts, `pseudos/`, created by the same LUMI user from 12:32 on). Not read or modified. My work lives in `GaP_t1/haiku_run/` (moved there at 12:35).
- SCF (22864746) done in ~7 s: 24 sym ops, 29 k-points, highest occupied level 7.6383 eV, zero forces (confirms GaP internal coordinates fixed by symmetry).
- Job 22865005 (ph.x ldisp 4x4x4 + NSCF 8x8x8, nbnd 20) submitted.
- Job 22865010 (ph.x ldisp 4x4x4 + NSCF 8x8x8, nbnd 20): COMPLETED, 12m31s on 64 cores.
  - Gamma phonons (raw, before ASR): T2 359.2 cm-1 (x3); acoustic -4.4 cm-1 (ASR violation, to be removed with dynmat.x). LO/TO not yet separated (ph.x epsil at Gamma: check the LO line).
  - Gamma bands (eV, absolute QE frame): 3d -6.92(x3), -6.82(x2); P3s -4.87; VBM 7.6383 (x3); CB 9.4745 (Gamma1), 11.527 (x3), 16.46, 17.37(x2), 20.10(x3). Gap 1.64 eV (indirect, CBM off Gamma).
- Wannier choice: 10 WF = Ga:sp3s* + P:sp3s*; exclude bands 1-5 (3d); nbndsub 10 (= 4 valence + 6 conduction); disentangle window -5.5..19.0 eV, frozen -5.5..11.0 eV.
  Concern: 10 sp3s* WF may not reproduce conduction bands to ~6 eV above the gap (up to ~15 eV absolute); the Wannier-vs-DFT comparison will decide. If poor, add projections and rerun.
- Job 22866574 (EPW 48^3 with wannierize=.true., lindabs, nqf=1) submitted in haiku_run/epw48.
- Job 22869825 (SCF refresh + ph.x ldisp 4x4x4 WITH fildvscf + full-grid NSCF 8x8x8 nosym, 512 k): COMPLETED, 10 min 8 s, 64 cores. ph.x was re-run because the first DFPT did not write dvscf (fildvscf not set).
- Full-grid NSCF is required by EPW wannierize ("inconsistent nscf and elph k-grids" otherwise): nkstot must equal nk1*nk2*nk3.
- EPW input fixes learned: bands_skipped='exclude_bands = 1-5' (not nbndskip); no mp_mesh_k with unshifted grid; projections sp3s* not parsed by wannier90 here -> Ga:sp3, P:sp3 (8 WF). dvscf/dyn needed as symlinks in dvscf_dir (gap.dvscf_qN, gap.dyn0, gap.dyn_qN) AND gap.dyn0 in the EPW run directory (ph's irreducible-q order; without it EPW's q-order differs and dynmat_asr fails at q4).
- Wannier (8 sp3, 15 bands, window -5.5..19, froz -5.5..11): final spread 22.16 A^2 total.
- Job 22870829 / 22871447: EPW 48^3 (lindabs, nqf=1, omega 0-6 eV step 0.02, degaussw 0.025 eV). 22871447 COMPLETED 8 min, wrote Gamma_alphabeta_s.dat (909 lines, 3 optical mode blocks x 301 energies; row at 0 eV is NaN (1/omega^2)).
- dynmat.x (asr='simple') on Gamma dyn1: acoustic 0 cm-1; optical T2 (G15) 359.17 cm-1 = 10.7675 THz = 44.53 meV, IR-active. (No LO-TO split at q=0 without NAC.) asr='none' aborted in dynmat.x; raw ph.x acoustic = -4.4 cm-1.
- Peak (48^3, invariant I_s = sqrt(sum_ab |Gamma^ab|^2), total = sum over the T2 triplet): 2.86 eV, total 28.78 A^2/eV, dominant mode T2 at 44.53 meV (10.768 THz). Degenerate modes individually differ ~7% (basis effect); the summed invariant is the basis-independent number.
- Jobs queued: 22872306 (EPW 96^3, epwread, nqf=1), 22872321 (DFT bands path + Wannier bands via wannier90 restart=plot).

## Final state (2026-10-15, 12:53 UTC)
- Adopted mesh 96x96x96 (EPW 22872463), kernel = kernel/Gamma_alphabeta_s.dat (= kernel/Gamma_alphabeta_s_96.dat). 48^3 kernel kept as kernel/Gamma_alphabeta_s_48.dat.
- Peak (invariant = sum over modes of sqrt(sum_ab |Gamma|^2)): 2.82 eV, 29.79 A^2/eV (96^3); 2.86 eV, 28.78 A^2/eV (48^3).
- 128^3 check: 1-node run OOM (22873069); 2-node retry (22873912) pending on priority, cancelled before start. Not completed.
- Wannier vs DFT: valence 3-6 meV RMS; lowest conduction 26 meV RMS; higher conduction 100-255 meV RMS (8-WF sp3 model limitation; sp3s* not accepted by wannier90 here).
- Gamma phonons: T2 359.17 cm-1 (10.7675 THz), acoustic 0 with ASR. No LO-TO split at q=0.
- node_hours 0.654 (jobs.log); wall ~4.8 h.
- Decisions: invariant definition (Frobenius per mode, summed over modes); degaussw 0.025 eV; tr2_ph 1e-14; scalar-relativistic mode.
- Not done: independent check of the v1 kernel; a finer mesh that converges the peak position.
