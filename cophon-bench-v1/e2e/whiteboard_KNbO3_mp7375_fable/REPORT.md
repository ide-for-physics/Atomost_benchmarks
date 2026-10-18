# REPORT — light-induced coherent-phonon generation kernel of KNbO3 (mp-7375, sealed R3m cell)

cophon-bench v1, whiteboard arm, model fable. All numbers below are traceable to files in this folder
(`inputs/`, `dft/`, `wannier/`, `epw_out/`, `kernel/`, `jobs.log`, `NOTES.md`).

## 1. What was computed

Second-order coherent-phonon generation kernel Gamma^{ab}_s(omega_s; omega, -omega) of Hu, Guo, Li, Wang, Chang
(manuscript Eq. for Gamma^{alpha beta}_s, SI Sec. II/IV), as implemented in the authors' kernel variant of EPW
(toolchain `qe-phnlo-75`, `EPW/src/indabs.f90`, driver flag `lindabs`): the double-resonant triangle diagram (c)
with Gaussian electronic resonance of width `degaussw` = 0.025 eV (the paper's eta), phonon-resonant denominator
1/(hbar omega_s + eps_lj + i eta), prefactor i pi/(hbar omega)^2, output in Å²/eV per mode and Cartesian channel
(xx, yy, zz, xy, xz, yz, yx, zx, zy; real and imaginary parts), photon energies 0.02–6.00 eV in steps of 0.02 eV,
all Γ-point optical modes s = 4..15. The build does not evaluate diagram (e) (`lgammae` is declared but out of scope
in this version), so the kernel file contains diagram (c) only — the same quantity the code writes for every material.

Rotational invariant used for RESULT.json: for each mode s and photon energy E,
I_s(E) = sum over the 9 Cartesian channels (a,b) of |Gamma^{ab}_s(E)|  [Å²/eV]
(the per-mode magnitudes summed over Cartesian channels). `peak_ev` is the E in [0, 6] eV maximising I_s(E) over all
modes, `peak_a2_per_ev` the value, `mode_thz` / `mode_irrep` the mode s at that maximum. The script
`inputs/analyze_kernel.py` re-derives these numbers from `kernel/Gamma_alphabeta_s.dat`.

## 2. Structure and DFT setup

* Cell: the sealed cell exactly as given (POSCAR vectors; the CIF describes the same cell, a = 4.005020 Å,
  alpha = 89.8916°). Note: the vector ordering (a1, a2, a3) is left-handed (dynmat.x warns); QE/EPW use |V| and the
  Cartesian frame is unchanged, so the sealed ordering was kept. No vc-relax.
* Internal coordinates: forces at the given positions are < 4e-5 Ry/Bohr (`dft/scf.out`), below any sensible
  relaxation threshold, so the positions were used as given (no relaxation).
* Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (K 9 e, Nb 13 e, O 6 e), scalar-relativistic use (no SOC);
  ecutwfc = 90 Ry, ecutrho = 360 Ry (Dojo "normal" hints 74/82/84 Ry). PBE, fixed occupations.
* SCF: 8x8x8 Monkhorst-Pack (65 irreducible k, C3v: 6 symmetry operations), conv_thr 1e-10.
  Gap on the 8x8x8 grid: VBM 8.4109 eV, CBM 10.6171 eV, Eg = 2.206 eV (indirect; direct gap at Γ 3.09 eV).
* Band groups (Γ): 11 semicore bands (Nb 4s, Nb 4p, K 3s, K 3p, O 2s; top at -2.28 eV), O 2p 3.3–8.4 eV (9 bands),
  Nb 4d t2g from 10.62 eV, eg from 14.2 eV, K 4s/Nb 5s/O 3s-like from 15.2 eV, interstitial bands 16.5–20 eV.

## 3. Γ phonons (DFPT, `dft/ph.out`, `dft/dynmat.out`)

ph.x at q = Γ (ldisp with a 1x1x1 grid, tr2_ph = 1e-16, epsilon and Z* computed), acoustic sum rule 'crystal' via
dynmat.x (||dyn(ASR) - dyn|| = 2.3e-3, acoustic modes -3.3/1.6 cm⁻¹ before ASR -> 0.00 after).
Mode symmetry (C3v, ph.x) and frequencies with ASR (dynmat.x; the EPW fine-mesh phonon energies are identical,
e.g. mode 9 = 29.42 meV):

| mode | irrep | cm⁻¹ | THz | meV | IR activity (D/Å)²/amu |
|---|---|---|---|---|---|
| 1–3 | E + A1 (acoustic) | 0.00 | 0.000 | 0.00 | 0 |
| 4, 5 | E | 183.15 | 5.491 | 22.71 | 2.24 |
| 6 | A1 | 186.22 | 5.583 | 23.09 | 0.003 |
| 7, 8 | E | 202.17 | 6.061 | 25.07 | 51.5 |
| 9 | A1 | 237.30 | 7.114 | 29.42 | 39.4 |
| 10 | A2 | 248.28 | 7.443 | 30.78 | 0 (silent) |
| 11, 12 | E | 275.31 | 8.253 | 34.13 | 0.001 |
| 13, 14 | E | 518.22 | 15.536 | 64.25 | 31.5 |
| 15 | A1 | 570.91 | 17.115 | 70.79 | 28.5 |

eps_inf = diag(5.584, 5.584, 5.181); Z*(K) = 1.17 (xx), 1.15 (zz).
Coarse q-mesh for EPW = Γ only (1x1x1): the kernel needs g only at q = Γ, where the phonon-side Wannier
interpolation is exact (single R_p = 0); the electron-side interpolation uses the 8x8x8 coarse k-mesh.

## 4. Wannier interpolation (`wannier/`, `epw_out/epw1.out`)

21 Wannier functions (O:p ×9, Nb:d ×5, Nb:s, K:s, K:d ×5) from bands 12–50 of the 8x8x8 NSCF (bands 1–11 excluded);
disentanglement outer window [2, 30] eV, frozen window [2, 17.5] eV (= CBM + 6.9 eV; at most 17 bands inside, at
least 27 in the outer window), dis_num_iter 2000, num_iter 1000, use_ws. Final spreads: O p 0.65–0.72 Å², Nb d
1.13–1.27 Å², Nb s 2.29 Å², K s 1.88 Å², K d 1.94–2.24 Å², total 26.77 Å².

DFT (`dft/bands.out`, pw.x `bands`) vs Wannier-interpolated bands (`wannier/kno_band.dat`) along
Γ–X–M–Γ–R–X (pseudo-cubic labels in the rhombohedral reciprocal basis, 221 DFT / 264 Wannier k-points;
comparison data in `wannier/bands_compare.dat`, script `inputs/compare_bands.py`):

| window | RMS deviation | max deviation |
|---|---|---|
| valence, O 2p manifold (9 bands, 3.3–8.4 eV) | 0.83 meV | 6.9 meV |
| conduction up to CBM + 3 eV | 1.00 meV | 5.3 meV |
| conduction up to CBM + 4 eV | 0.98 meV | 5.3 meV |
| conduction up to CBM + 6 eV | 1.84 meV | 13.7 meV |

## 5. Kernel: fine-mesh convergence (`kernel/`)

EPW kernel runs (epwread from the Wannier data, full fine k-mesh without symmetry reduction, nqf = Γ, efermi_read
mid-gap 9.51 eV, degaussw 0.025 eV, no adaptive smearing, fsthick = 1e10 so all 21 bands enter, eps_acoustic 5 cm⁻¹):

Dominant mode at every mesh: mode 9 (A1, 237.30 cm⁻¹ = 7.114 THz = 29.42 meV). I_9(E) = sum_ab |Gamma^{ab}_9(E)|:

| fine mesh | file | peak E (eV) | peak I_9 (Å²/eV) | I_9 at 3.6 / 3.8 / 4.0 eV | ∫₀⁶ I_9 dE (Å²) | wall (1 node) |
|---|---|---|---|---|---|---|
| 12³ (smoke test) | `kernel/Gamma_alphabeta_s_12x12x12.dat` | 3.44 | 128.9 | 44.9 / 108.9 / 60.2 | 135.9 | (in Wannier run) |
| 24³ | `kernel/Gamma_alphabeta_s_24x24x24.dat` | 3.84 | 86.7 | 83.8 / 76.5 / 68.8 | 135.6 | 3m52s |
| 32³ | `kernel/Gamma_alphabeta_s_32x32x32.dat` | 3.74 | 88.0 | 79.6 / 74.2 / 67.6 | 135.6 | 7m58s |
| 48³ | `kernel/Gamma_alphabeta_s_48x48x48.dat` | 3.62 | 79.8 | 79.0 / 74.7 / 67.6 | 135.6 | 26m45s |
| 64³ | `kernel/Gamma_alphabeta_s_64x64x64.dat` | 3.66 | 80.4 | 79.2 / 77.4 / 68.0 | 135.6 | 1h00m |
| **96³ (adopted)** | `kernel/Gamma_alphabeta_s.dat` (= `..._96x96x96.dat`) | **3.64** | **79.97** | 79.4 / 76.5 / 68.5 | 135.6 | 2h08m (2 nodes) |

The energy-integrated kernel weight is converged already at 24³; the point-wise spectrum (25 meV Gaussian
resonances in 3D) needs ≥ 48³: between 48³ and 64³ the peak value changes by 0.8 % and the peak energy by 0.04 eV on
one broad maximum (I_9 ≥ 76.8 Å²/eV for 3.58–3.80 eV at 64³); the mean point-wise change |I64 − I48|/max over
3–6 eV is 1.6 % (max 6–8 %) for the three strongest modes (9, 15, 6). The confirmatory 96³ run agrees with 64³ to
0.6 % in the peak value and 0.02 eV (one grid step) in the peak energy. Adopted converged mesh: **96x96x96**
(the finest; 64³ would give peak_ev 3.66, peak 80.43 Å²/eV, i.e. the same answer within the stated tolerance).

Symmetry check (64³, mode 9, A1, at the peak): |Gamma^xx| = |Gamma^yy| = 26.0, |Gamma^zz| = 28.4, all off-diagonal
channels < 0.03 Å²/eV, as required by C3v for an A1 mode (SI Sec. IV, BaTiO3 analysis). The E modes (4/5, 7/8, 11/12,
13/14) come in degenerate pairs with equal invariants; the A2 mode 10 is silent (I ≤ 0.6 Å²/eV).

Per-mode maxima of the invariant on the converged mesh (0–6 eV):

| mode | irrep | THz | E of max I_s (eV) | max I_s (Å²/eV) | largest channel |
|---|---|---|---|---|---|
| 4, 5 | E | 5.492 | 3.32 | 8.96 / 8.95 | yx / xx 3.41 |
| 6 | A1 | 5.583 | 3.64 | 15.24 | zz 5.54 |
| 7, 8 | E | 6.060 | 3.32 | 23.92 / 23.91 | yx / yy 9.15 |
| **9** | **A1** | **7.114** | **3.64** | **79.97** | zz 28.8 (xx = yy 25.9) |
| 10 | A2 | 7.410 | 3.58 | 0.56 | xy 0.26 |
| 11, 12 | E | 8.229 / 8.239 | 3.32 | 11.00 / 11.03 | yx / yy 4.25 |
| 13, 14 | E | 15.544 / 15.550 | 5.30 | 6.27 / 6.27 | xz / yz 1.73 |
| 15 | A1 | 17.130 | 5.30 | 31.44 | yy 10.65 |

RESULT.json therefore reports peak_ev = 3.64, peak_a2_per_ev = 79.965, mode_thz = 7.1144 (EPW fine-mesh phonon
energy 29.423 meV; dynmat.x 237.30 cm⁻¹ = 7.114 THz), mode_irrep = A1 (the ferroelectric-type Nb–O stretching A1 mode
of the R3m perovskite). The E-mode pairs are degenerate to < 0.2 % as they should be (no symmetrisation is applied by
the code; the full 96³ mesh respects the point group).

Other diagnostics: no NaN/Inf rows in any kernel file; the kernel sets in at 3.02 eV, i.e. at the minimum direct gap
(3.09 eV on the 8x8x8 grid, at Γ) minus the Gaussian tail, as expected for a resonant (delta-function) kernel with a
25 meV width (the indirect gap, 2.21 eV, does not enter); the file `Pi_0.dat` (field-free phonon self-energy) is
written alongside by the code (`epw_out/`).

## 6. Compute

From `jobs.log` (node-hours = Slurm AllocCPUS/256 × elapsed; 256 hyperthreads = 128 cores per LUMI-C node):

| job | purpose | partition | node-hours |
|---|---|---|---|
| 22922824 | SCF test | debug | 0.001 |
| 22922838 | SCF + ph.x Γ + dynmat.x | debug | 0.033 |
| 22922889 | SCF + NSCF 8x8x8 + bands + projwfc | debug | 0.009 |
| 22922922 | EPW Wannierisation + epwwrite + 12³ smoke test | debug | 0.153 |
| 22923073 | EPW kernel 24³ | debug | 0.064 |
| 22923107 | EPW kernel 32³ | debug | 0.133 |
| 22923078 | EPW kernel 48³ | small | 0.446 |
| 22923079 | EPW kernel 64³ | small | 1.003 |
| 22924174 | EPW kernel 96³ (2 nodes) | small | 4.260 |
| **total** | | | **6.10 node-hours** (budget 20) |

Wall clock: start 2026-10-16 22:27 UTC (first command) to DONE 2026-10-17 ≈ 04:15 UTC ≈ 5.8 h, of which ≈ 2.5 h were
queue waits on `small` (the `standard` estimate was 41 h, so `small` was chosen; `debug` was used only for runs
expected under 10 minutes, one at a time). Human touches: 0.

## 7. Files

* `RESULT.json` — declared result; `kernel/Gamma_alphabeta_s.dat` — converged (96³) kernel as written by epw.x;
  `kernel/Gamma_alphabeta_s_<mesh>.dat` — coarser meshes; `kernel/*_invariant.dat` — I_s(E) per mode (derived).
* `inputs/` — every input used: `scf.in` (= `scf0.in`), `nscf.in` (512-point list), `bands.in`, `projwfc.in`,
  `ph.in`, `dynmat.in`, `epw1.in` (Wannierisation + epwwrite), `epw_nk{24,32,48,64,80,96}.in` (kernel runs; 80³ was
  prepared but not run), Slurm scripts `job_*.sbatch`, analysis scripts (`compare_bands.py`, `analyze_kernel.py`,
  `compare_meshes.py`, `make_result.py`, `proj_character.py`). `relax.in` was prepared but not run (forces already
  < 4e-5 Ry/Bohr).
* `wannier/` — `kno.win` (wannier90 input generated by EPW), `kno.wout`, `kno_band.dat/.kpt/.labelinfo.dat`,
  `bands_compare.dat` (DFT vs Wannier along the path).
* `dft/` — `scf.out`, `nscf.out`, `bands.out`, `projwfc.out`, `ph.out`, `dynmat.out`.
* `epw_out/` — `epw1.out` (Wannierisation run), `epw_nk*.out` (kernel runs), `Pi_0.dat`, `decay.*`.
* `jobs.log`, `NOTES.md` (running log and decisions), `DONE`.
* Remote root: `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/KNbO3_mp7375/fable_v1/`
  (wavefunctions deleted after use; EPW restart files and `save/` kept).
