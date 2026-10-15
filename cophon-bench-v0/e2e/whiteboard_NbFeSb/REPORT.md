# NbFeSb: light-induced coherent-phonon generation kernel Gamma^{ab}_s(omega_s; omega, -omega) — REPORT

Crystal: half-Heusler NbFeSb, F-43m (T_d), fcc primitive cell a = 4.20116 A (conventional a = 5.94134 A), 3 atoms
(`structure.cif` = `structure_POSCAR`). All Cartesian components below refer to the cubic axes of the given POSCAR cell.

## 1. Headline result
**Peak photon energy: 3.27 eV** (total over the six optical modes and every individual mode peak between 3.270 and
3.275 eV on a 5 meV photon grid; 3.275 eV on the 25 meV grid for every k-mesh tested). Peak FWHM 0.17 eV.
**Dominant phonon mode: the upper T_2 optical triplet, 263.3 cm-1 = 7.894 THz (32.62 meV), modes 7-9** (the lower
T_2 triplet at 204.8 cm-1 = 6.140 THz contributes about 70 % of the upper one). Both triplets are T_2 of T_d (IR + Raman active).
**Value of the rotational invariant at the peak (fixed broadening 25 meV, densest mesh 96^3, 3.270 eV, in A^2/eV):**
| quantity | modes 7-9 (263 cm-1) | modes 4-6 (205 cm-1) | all six optical modes |
|---|---|---|---|
| S1_s = sum_ab |Gamma_s^ab| per mode (code's eigenvector basis) | 23.56 / 23.81 / 19.89 | 16.64 / 13.13 / 17.10 | - |
| F_s = sqrt(sum_ab |Gamma_s^ab|^2) per mode (basis-independent) | 12.18 / 12.48 / 12.30 | 8.04 / 8.19 / 8.38 | - |
| sum over the triplet of S1_s | 67.26 | 46.87 | 114.13 |
| sqrt(sum over the triplet of F_s^2) | 21.34 | 14.21 | 25.64 |
| single off-diagonal channel of a symmetry-adapted partner, |Gamma^{xy}| = |Gamma^{yx}| (= sqrt(sum F^2 / 6)) | 8.71 | 5.80 | - |
The largest single-mode value is S1 = 23.8 A^2/eV (mode 8, dominated by |Gamma^{xy}| = |Gamma^{yx}| = 8.3 A^2/eV).
Kernel computed with the authors' kernel variant of EPW (triangle diagram Gamma_c, see Sec. 2), electronic broadening
0.025 eV, fine k-mesh 96^3 (converged: see Sec. 5). Source: `results/kernel/k96_zoom/Gamma_alphabeta_s.dat` (5 meV grid,
3.0-3.6 eV) and `results/kernel/k96/Gamma_alphabeta_s.dat` (25 meV grid, 0.025-6.0 eV); invariants via
`scripts/kernel_invariants.py` -> `results/kernel/<mesh>/<mesh>_S1_vs_omega.dat`.
Definition used for "rotational invariant": the task's wording (per-mode magnitude summed over the Cartesian channels) is taken
literally as S1_s(omega) = sum over the nine channels ab of |Gamma_s^{ab}(omega)|; the Frobenius norm F_s and the sum over the
degenerate triplet are given as well because the partition of a T_2 triplet into partners depends on the (arbitrary) eigenvector
basis of the dynamical-matrix diagonalizer, while F_s and the triplet sums do not. All of them peak at the same photon energy.

## 2. What was computed (method, as actually run)
- DFT: Quantum ESPRESSO 7.5 (toolchain `qe-phnlo-75` on LUMI), PBE, PseudoDojo nc-fr-04 standard pseudopotentials used
  scalar-relativistically (no SOC), ecutwfc = 90 Ry / ecutrho = 360 Ry, SCF k-mesh 10x10x10, fixed occupations.
  44 electrons = 22 occupied bands (13 semicore + 9 valence). PBE gap 0.527 eV (VBM 16.4886 eV at L, CBM 17.0158 eV at X).
  Files: `inputs/scf.in`, `results/dft/scf.out`.
- DFPT: ph.x at q = Gamma (ldisp with a 1x1x1 q-grid, epsil = .true., tr2_ph = 1e-16); dynmat.x with asr = 'crystal'.
  Files: `inputs/ph.in`, `inputs/dynmat.in`, `results/phonons/ph.out`, `results/phonons/dynmat.out`.
- Wannier/EPW: NSCF on the full 10x10x10 grid (1000 k, `inputs/nscf.in`), Wannierization inside EPW (wannier90 library),
  22 Wannier functions (Nb s,p,d; Fe s,p,d; Sb s,p), frozen window to CBM+9 eV, see Sec. 4. Files: `inputs/wanC22/epw_coarse.in`, `results/epw/wanC22/nbfesb.wout`.
- Kernel: the authors' modified EPW ("kernel variant", `EPW/src/indabs.f90`, driver flag `lindabs`). This build implements
  the triangle (Raman-like) diagram (c) of the manuscript, Gamma_c, plus the field-free phonon self-energy Pi_0; the
  optically-perturbed-EPC diagram (e) (`lgammae`) is declared "out of scope in v1" in the source and is NOT computed.
  Electronic broadening degaussw = 0.025 eV (paper value; Gaussian delta), photon energies 0.025-6.0 eV in 0.025 eV steps
  (omega = 0 is excluded because of the 1/omega^2 prefactor), q = Gamma only, all Wannier bands in the band sums
  (fsthick = 100 eV), T = 0 occupations with E_F at mid-gap (16.7522 eV). Output file: `Gamma_alphabeta_s.dat`
  (photon energy in eV; Re/Im of the xx, yy, zz, xy, xz, yz, yx, zx, zy components in A^2/eV; one block per optical mode).

## 3. Gamma phonons from DFPT (acoustic sum rule applied, dynmat.x asr='crystal')
| modes | irrep (T_d) | freq (cm-1) | freq (THz) | energy (meV) | IR activity ((D/A)^2/amu) |
|---|---|---|---|---|---|
| 1-3 | T_2 (acoustic) | 0.00 | 0.000 | 0.00 | 0 |
| 4-6 | T_2 (optical, IR+Raman) | 204.81 | 6.1399 | 25.394 | 1.80 |
| 7-9 | T_2 (optical, IR+Raman) | 263.32 | 7.8942 | 32.649 | 29.80 |
Raw DFPT before ASR: acoustic 5.79 cm-1, optical 204.81 / 263.41 cm-1 (`results/phonons/ph.out`). ||dyn(ASR)-dyn|| = 1.2e-3.
eps_inf = 24.43; Born charges (ASR): Nb +5.053, Fe -7.623, Sb +2.571. With a q direction (q || x, `dynmat_LO.out`) the LO
partners are 207.33 cm-1 (6.216 THz) and 347.73 cm-1 (10.425 THz); the kernel uses the exact-Gamma (TO-degenerate) modes.
Both optical triplets are T_2, so every optical mode is both IR and Raman active; the kernel of a T_2 mode polarized along
z lives in the xy/yx channels (and cyclic permutations), which is what the computed tensors show (Sec. 5).

## 4. Wannier interpolation quality
Model adopted: 22 Wannier functions, projections Nb s,p,d + Fe s,p,d + Sb s,p, the 13 semicore bands excluded,
disentanglement window 4.0-36.0 eV, frozen window 4.0-26.0 eV (VBM = 16.49 eV, CBM = 17.02 eV, so the frozen window
reaches CBM + 9.0 eV), 2000 disentanglement + 1000 maximal-localization iterations, total spread 42.1 A^2 (largest
single spread ~3 A^2). Coarse grid 10x10x10 (1163 Wigner-Seitz vectors). Input: `inputs/wanC22/epw_coarse.in`; wannier90
log `results/epw/wanC22/nbfesb.wout`.

DFT (pw.x, `results/dft/bands.out`) versus Wannier-interpolated (EPW band_plot, `results/epw/wanC22/band.eig`) bands on the
same 153-point path G-X-W-K-G-L-U-W-L-K (`inputs/kpath_epw.kpt`), per-k band ordinals matched, absolute energies:
| window (eV, absolute) | meaning | (k,band) pairs | RMS dev. (meV) | max dev. (meV) |
|---|---|---|---|---|
| 5.0 - 23.02 | all valence (incl. Sb 5s) + conduction up to CBM+6 eV | 2312 | 0.61 | 4.88 (band 28 at 21.6 eV, k#85) |
| 5.0 - 16.5 | valence bands only | 1377 | 0.53 | 2.89 |
| 17.0 - 23.02 | conduction up to CBM+6 eV | 935 | 0.71 | 4.88 |
Per-pair data: `results/epw/wanC22/band_compare_5.0_23.02.dat` (and the other windows); script `scripts/band_compare.py`.
Two smaller models were tried and rejected (A16 = Nb s,d + Fe s,d + Sb s,p: RMS 9.2 meV / max 155 meV because band 28 lies
above its frozen window; B19 = A16 + Fe p: disentanglement failed, RMS 62 meV); summary `results/epw/band_compare_summary.txt`.

## 5. Kernel results and k-mesh convergence
### 5.1 Spectrum
The kernel is zero below the direct gap (~1.1 eV; Gaussian tails only), becomes non-negligible from 1.25 eV, and the total
S1 (96^3) shows its global maximum at 3.27 eV (114 A^2/eV), a shoulder near 3.15 eV (54), secondary maxima at
1.725 eV (42) and 1.925 eV (34), and values of 10, 2 and 3 A^2/eV at 4, 5 and 6 eV. All six optical
modes share the same peak energy (every mode is driven by the same cluster of electronic critical points: vertical
transitions 22->27 at X (3.269 eV), 20->25 at L (3.248 eV), 18->23/24 on Gamma-L and 19->24 on K-Gamma of the DFT bands).
Only off-diagonal channels are significant for every mode (|xx|,|yy|,|zz| <= 0.44 vs 8.7 A^2/eV at the peak), as required for
T_2 modes in T_d: a mode polarized along z couples the xy/yx channels, and cyclic permutations.
Files: `results/kernel/k96/Gamma_alphabeta_s.dat` (adopted), `k80`, `k64`, `k48`, `k24` (same grid), `k96_zoom`, `k64_zoom`
(5 meV grid), `k64_adsmear` (adaptive smearing). `Pi_0.dat` (field-free phonon self-energy) is written alongside each.

### 5.2 Fine k-mesh convergence (fixed broadening 0.025 eV; identical inputs apart from nkf1=nkf2=nkf3)
| fine mesh | k-points | peak omega (25 meV grid) | total S1 at 3.275 eV | triplet S1 (4-6 / 7-9) | rel. RMS of total S1 over 1-6 eV vs 96^3 | wall time (1 node) |
|---|---|---|---|---|---|---|
| 24^3 | 13 824 | 3.275 | 114.49 | 45.39 / 69.10 | 10.1 % | 1.9 min |
| 48^3 | 110 592 | 3.275 | 114.30 | 47.01 / 67.29 | 1.75 % | 14 min |
| 64^3 | 262 144 | 3.275 | 114.05 | 46.92 / 67.13 | 0.79 % | 30 min |
| 80^3 | 512 000 | 3.275 | 113.99 | 46.91 / 67.07 | 0.58 % | 59 min |
| 96^3 (adopted) | 884 736 | 3.275 | 114.11 | 46.89 / 67.22 | 0 | 99 min |
Peak value changes by 0.3 % (48^3 -> 64^3), 0.06 % (64^3 -> 80^3) and 0.1 % (80^3 -> 96^3); the per-mode peak energy is
3.275 eV on every mesh. Zoom runs (3.0-3.6 eV, 5 meV): peak at 3.275 eV on 64^3 (114.05) and 3.270 eV on 96^3 (114.13),
the two adjacent grid points differing by 0.02 %; the zoom spectra of 64^3 and 96^3 differ by 0.3 % RMS. Convergence
data: `results/kernel/mesh_convergence.txt` (from `scripts/mesh_convergence.py`).
Cross-check with the code's adaptive smearing (`ladsmear = .true.`, 64^3, `results/kernel/k64_adsmear`): peak at 3.250 eV
with total S1 = 138.6 A^2/eV (the adaptive width is smaller than 25 meV over most of the zone, so the resonance is
sharper/taller); the peak position agrees within one 25 meV step. The fixed 25 meV broadening of the paper is the adopted result.

### 5.3 Convergence with respect to the band set
The band sums run over all 22 Wannier bands (fsthick = 100 eV; EPW used ibndmin = 1, ibndmax = 22). The paper's test
(SnSe, SI Fig. S-bndtest) found no visible dependence on the number of conduction bands; here the model reaches CBM + 9 eV
in the frozen window and CBM + 19 eV in the outer window, which contains every resonant pair for photon energies <= 6 eV.

## 6. Compute used
Total LUMI compute: **6.46 node-hours** (12 Slurm jobs, all on the `standard` partition, 1 exclusive 128-core node each;
listed one per line with job id, purpose and node x hours in `jobs.log`; summed by `scripts/sum_nodehours.py`).
Breakdown: SCF+bands+projwfc 0.008; ph.x Gamma 0.029; NSCF 0.009; EPW Wannierization (3 models) 0.674; kernel runs
24^3 0.032, 48^3 0.233, 64^3 0.500, 80^3 0.985, 96^3 1.652; zoom 64^3 0.315, zoom 96^3 1.026; adaptive-smearing 64^3 0.998.
Budget was 20 node-hours; about one third was used. No debug-partition jobs were run. Large scratch files (NSCF/SCF
wavefunctions) were deleted on LUMI after the last run; the Wannier-representation data and all outputs were kept
under the remote root `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/NbFeSb/`.

## 7. Files
- Inputs: `inputs/scf.in`, `inputs/bands.in`, `inputs/nscf.in`, `inputs/projwfc.in`, `inputs/ph.in`, `inputs/dynmat.in`,
  `inputs/dynmat_LO.in`, `inputs/wan*/epw_coarse.in` (EPW coarse + Wannierization; the wannier90 input is generated by EPW
  from it and saved as `results/epw/<model>/nbfesb.win`), `inputs/fine_k*/epw_fine.in` (kernel runs), Slurm scripts `inputs/job_*.sh`.
- Outputs: `results/dft/`, `results/phonons/`, `results/epw/<model>/` (band.eig, nbfesb.wout), `results/kernel/k<N>/Gamma_alphabeta_s.dat`
  and `Pi_0.dat`, invariants in `results/kernel/k<N>/*_S1_vs_omega.dat`; Wannier-vs-DFT comparison `results/epw/<model>/band_compare_*.dat`.
- `jobs.log` (one line per Slurm job), `NOTES.md` (decisions and running log).
