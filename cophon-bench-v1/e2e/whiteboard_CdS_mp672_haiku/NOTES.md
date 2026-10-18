# NOTES: CdS_mp672 light-induced coherent-phonon kernel (cophon-bench v1, whiteboard)

## Decisions (initial, with reasons)
- Cell: used exactly the sealed cell from structure_POSCAR (cell parameters and crystal positions as given). No vc-relax.
- Pseudos: PseudoDojo nc-fr-04 PBE standard, fully relativistic UPF, used scalar-relativistically (no SOC), as the task allows.
  Cutoff: ecutwfc = 100 Ry, ecutrho = 400 Ry (PseudoDojo "normal" hint: Cd 102 Ry, S 52 Ry).
- Electrons: scf/nscf k-grid 6x6x4 (coarse, EPW/W90 grid), nbnd = 40 (26 occupied + 14 empty).
- Phonons: ph.x at Gamma only (no q-mesh). EPW run with nq = 1x1x1 so that the fine q-loop is Gamma only.
- Kernel code: /EPW/src/indabs.f90 (kernel variant). Its Gamma_alphabeta_s is reset per q and written only at iq == lastq
  (see indabs.f90 ~L574 and use_wannier.f90 ~L1393). So nqf = 1x1x1 is REQUIRED so the written kernel is the Gamma phonon.
- Photon grid: omegamin must be > 0 (the kernel has 1/omega^2; omega = 0 gives a singular point), so the grid starts at 0.01 eV.
- degaussw = 0.025 eV (the paper's eta).

## Log
- 18:29 DFPT first job 22880700 failed at launch (interconnect errors on 4 nodes); cancelled, resubmitted as 22881430.
- 18:40 22881430 also failed at srun launch (interconnect, nodes nid002442-43); cancelled. Resubmitted as 22881635 pinned to --nodes=1 --ntasks=64.
- DFPT Gamma (22881635) done: ASR-corrected Gamma modes (cm-1): 36.3 E2, 134.9 B1, 235.0 A1(IR), 241.3 E1(IR), 255.1 E2, 302.6 B1. dynmat.x asr=crystal output in ph/dynmat_asr.out. Staged dvscf/dyn to dvscf/ for EPW.
- EPW test: dis_win_max=15.5 eV gives 14 states in window < 16 WFs; raised to 18.0 eV (bands 21-37). Resubmitted as 22882125.
- W90 window: bands rise above 18 eV at some k; dis_win_max now 22.0 eV. Resubmitted test.
- EPW needs dvscf_dir/<prefix>.phsave/patterns.*.xml; staged from tmp/_ph0/cds.phsave.
- EPW dvscf expects dvscf_q1 + patterns (dvscf_star%open option of ph.x). Rerun ph2 -> writes dvscf dir.
- Test kernel ok (12x12x8). Convergence series: 24x24x16 (epw_k24), 36x36x24 (epw_k36), then 48x48x32 if affordable. Each in own dir; file names fixed by code.
- k24 peak 279 A2/eV (5.77 eV) vs test12 396 (5.69 eV): not converged; running k36.
- k36 peak 242 (5.73 eV) vs k24 279 (5.77): still moving 13%. Running k48x48x32.
- k48 peak 246.96 (5.77 eV) vs k36 242 (5.73): ~2% change; running k60x60x40 to confirm plateau.
- kernel convergence (global Frobenius peak): k12 396.0@5.69; k24 279.2@5.77; k36 242.0@5.73; k48 247.0@5.77
- k60 peak 238.6 (5.79 eV) vs k48 247.0 (5.77): -3.4%. Running k72x72x48.
- Kernel convergence (global Frobenius peak, Angstrom^2/eV; peak energy): 12x12x8 396.0 @5.69; 24x24x16 279.2 @5.77; 36x36x24 242.0 @5.73; 48x48x32 247.0 @5.77; 60x60x40 238.6 @5.79; 72x72x48 244.6 @5.78.
  Last three meshes agree within ~3%. Adopted mesh: 72x72x48 (finest run). Peak 244.6 A^2/eV at 5.78 eV, mode index 4 (E2 pair).
- Invariant definition used (paper does not state one explicitly): I_s(w) = [sum over 9 Cartesian channels |Gamma^{ab}_s(w)|^2]^(1/2) (Frobenius, rotationally invariant); peak = max over w in [0,6] eV and over s.
  Alternative (sum of channel magnitudes) is also in analysis/peak.py output if needed.
- Mode frequencies: DFPT Gamma after crystal ASR: E2 36.30 cm^-1 (1.088 THz); EPW reads 4.667 meV (1.128 THz) for the same pair (about 1.3 cm^-1 offset, not yet explained; EPW applies its own sum rule on the Gamma dyn).
- EPW wannier: 16 WF (Cd s,p; S s,p) on bands 21-40, exclude 1-20, dis_win_max 22 eV, dis_froz_max 10 eV, nbndsub 16.
- Wannier90 band plot via restart=plot rejected the eig layout twice; switched to EPW band_plot on the same explicit 85-point path as QE bands (path_list.dat).
- Band check (16 WF, dis 22 eV): valence RMS 14.6 meV max 125 meV (worst at L-H-A, bands 23-24); conduction <= CBM+6 RMS 135 meV max 410 meV. Not acceptable. Trying 20 WF (all bands, dis_win_max 23 eV, 12 random projections): epw_band20.

## Final summary (23:58 UTC, Oct 15 2026)
- Adopted kernel mesh: 72x72x48 -> kernel/Gamma_alphabeta_s.dat. Peak 244.58 A^2/eV at 5.78 eV, E2 pair (DFPT 36.30 cm^-1 = 1.088 THz). Mesh series in REPORT.md.
- Wannier interpolation misses the few-meV target: 16 WF valence RMS 14.6 meV (max 125 meV); conduction <= CBM+6 eV RMS 135 meV (max 410 meV). Attempts with 18/20 WF failed (W90 rejected 'random'; 18 WF crashed in the W90 interface). Reported as is; the kernel's conduction part carries this error.
- Phonons: Gamma DFPT with epsil; crystal ASR gives 0.00 cm^-1 for acoustic modes; optical modes 36.3-302.6 cm^-1.
- Compute: 4.26 node-h from sacct (my jobs only); the two `CdS_mp672_e2eH_rekernel_*` jobs on this account were not mine and are excluded.
- Open items: (1) improve the Wannier set (20 WF with a working projection scheme, or denser coarse k-grid) and rerun the kernel; (2) explain the 1.3 cm^-1 EPW vs DFPT offset for the E2 pair; (3) check the 2-5% E2 degeneracy residual.
