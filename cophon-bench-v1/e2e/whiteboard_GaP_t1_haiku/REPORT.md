# GaP_t1: light-induced coherent-phonon generation kernel (cophon-bench v1)

Numbers below match RESULT.json and kernel/Gamma_alphabeta_s.dat (96x96x96).

## Results
| quantity | value |
|---|---|
| peak photon energy (rotational invariant, 0-6 eV) | **2.82 eV** (96^3); 2.86 eV (48^3) |
| peak invariant, summed over the T2 triplet | **29.79 A^2/eV** (96^3); 28.78 A^2/eV (48^3) |
| dominant mode | optical T2 (G15) triplet, **10.7675 THz = 359.17 cm^-1 = 44.53 meV** |
| adopted mesh | 96x96x96 (fine k), coarse k 8x8x8, q 4x4x4, nqf = 1 (Gamma only) |
| cell | sealed fcc primitive cell of structure.cif (a_conv = 5.4472 A), no relaxation |
| node-hours | 0.654 (small partition, 64 cores per job, charged as half nodes) |
| wall hours | ~4.8 h (08:06 UTC start to 12:53 UTC) |

**Invariant definition (my choice, not given in the papers):** for each mode, I_s(w) = sqrt( sum_ab |Gamma^ab_s(w)|^2 ) over the nine Cartesian channels (Frobenius norm, rotationally invariant). The peak is the maximum over 0 < w <= 6 eV of the sum over modes, sum_s I_s(w). The three T2 modes are degenerate and their individual I_s differ by about 7% (basis choice), so only the summed value is quoted.

## Mesh convergence (kernel peak, EPW lindabs, degaussw = 0.025 eV, omega step 0.02 eV)
| fine mesh | peak (eV) | total invariant (A^2/eV) |
|---|---|---|
| 48x48x48 | 2.86 | 28.78 |
| 96x96x96 | 2.82 | 29.79 |

- The magnitude changes by 3.5% between 48^3 and 96^3. The peak position moves by 0.04 eV, two omega-grid steps. **This is not a fully converged peak position.**
- A 128^3 check was submitted, but it ran out of memory on one node (job 22873069), and the two-node retry (22873912) stayed pending on priority. It was cancelled before it started. No third mesh is available.

## Wannier interpolation quality
Wannier functions: Ga:sp3 + P:sp3 (8 WF), 15-band window (Ga 3d bands 1-5 excluded), disentanglement window -5.5..19.0 eV, frozen -5.5..11.0 eV, final total spread 22.16 A^2. DFT and Wannier bands compared along G-X-W-K-G-L (151 DFT points; wannier90 restart=plot). Deviations are per band index, with the DFT valence maximum at 7.638 eV and the conduction minimum at 9.280 eV (gap 1.64 eV).

| band | RMS (meV) | max (meV) |
|---|---|---|
| valence 1-4 (DFT 6-9) | 3.0, 5.6, 5.7, 5.0 | 8.0, 19.2, 20.6, 15.0 |
| conduction 5 (DFT 10) | 26 | 99 |
| conduction 6 (DFT 11) | 99 | 220 |
| conduction 7 (DFT 12) | 102 | 284 |
| conduction 8 (DFT 13) | 255 | 1000 |

Valence bands agree with DFT to a few meV. The lowest conduction band is at 26 meV RMS. **The higher conduction bands (up to about 6 eV above the gap) are not within a few meV**: the 8-function sp3 model is too small for them. The Gamma-point kernel depends on those conduction states, so this is a real limitation. An sp3s* (10-WF) model failed in wannier90 here ("Problem reading l state sp3s*"), so I did not get a better basis.

## Gamma phonons (DFPT, ph.x epsil = .true., tr2_ph = 1e-14, 4x4x4 q)
- Raw ph.x: acoustic -4.4 cm^-1, optical T2 359.2 cm^-1 (x3).
- dynmat.x asr='simple' on the Gamma dyn file: acoustic 0.00 cm^-1 (x3); optical T2 (G15) 359.17 cm^-1 (x3), IR-active.
- No LO-TO splitting at q = 0 (no non-analytic term in the Gamma dynamical matrix used by EPW).
- The DFPT and the NSCF both used forces = 0 (checked in the SCF): the internal coordinates are fixed by symmetry, so no relaxation was needed.

## Kernel and its limitations
- Kernel: Gamma_alphabeta_s.dat written by EPW/src/indabs.f90 (`indabs_main`, lindabs). Columns: omega (eV), then 9 complex channels (Re, Im) per row, one block per optical mode (modes 4-6; acoustic modes skipped). The omega = 0 row is NaN (1/omega^2 term), so only 0.02-6.00 eV is used.
- **Scope of the code:** the source header says "v1 scope": only the triangle diagram (Gamma_c) and Pi_0 are implemented; Gamma_e and Pi_kernel are out of scope. The authors' implementation note also lists unresolved issues: a missing ci factor in one vvmewan2bloch branch, and the eig_read/vvmef path being unsupported. The kernel values are therefore those of this v1 code and have not been checked against an independent calculation.
- Diagonal channels are ~1e-3 and off-diagonal ~0.2 (Re) at 1.9 eV. This is consistent with T2 symmetry in Td (the T2 response is off-diagonal), but I have not verified it beyond the symmetry argument.
- Broadening: degaussw = 0.025 eV (the paper's eta). Adaptive smearing off.

## Compute
- jobs.log lists each Slurm job: 16 completed or cancelled jobs (including failed attempts) and one cancelled pending job. Total 0.654 node-hours, against the 20-hour budget.
- The Wannier band plot ran wannier90 serially on the login node (a few seconds); it is not charged.
- The remote root `GaP_t1/` was shared with another run (directories 01_scf-04_epw). I did not read or modify its files, and I used `haiku_run/` for my work.
- Other jobs under the same LUMI account (CdS, InPS4, NbFeSb, Bi2O2Se, SnS2, and gap_wan2) belong to other runs. They were not touched.

## Deviations from the task sheet
- Scalar-relativistic use of the fully relativistic PseudoDojo UPF (allowed by the task).
- EPW needed the full 8x8x8 NSCF grid as an explicit nosym list, which is the "explicit NSCF k-point list" quirk.
- `epw96` linked its inputs from `epw48`; the 96^3 run wrote its kernel through the symlink into `epw48/Gamma_alphabeta_s.dat`. The 48^3 kernel was copied to `kernel/Gamma_alphabeta_s_48.dat` before that happened, and that copy is the one used here.
- Mesh convergence: two meshes (48^3, 96^3) only; see above.
