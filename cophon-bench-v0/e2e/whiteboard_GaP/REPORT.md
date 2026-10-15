# REPORT.md — light-induced coherent-phonon generation kernel of GaP (zincblende, structure as given)

Everything below is traceable to files in this folder (paths given in each section); the running log of decisions is NOTES.md.

## 1. Headline result
**The rotational invariant of the kernel is largest at a photon energy of 2.81 eV**, where it reaches
**10.17 A^2/eV per mode** (Frobenius norm sqrt(sum_ab |Gamma_s^ab|^2) of the 3x3 Cartesian tensor of one optical mode;
192^3 fine mesh: 10.16 / 10.15 / 10.18 A^2/eV for modes 4 / 5 / 6, photon-grid resolution 0.01 eV; a parabolic fit through
the three points around the maximum gives 2.814 eV; 168^3 gives 10.19 / 10.16 / 10.16 and 144^3 10.19 / 10.22 / 10.19). **The dominant (and only) optical phonon modes are the three degenerate components of the
T2 (Gamma_15) optical mode of zincblende GaP at 10.735 THz** (358.08 cm^-1 = 44.40 meV with the acoustic sum rule;
the LO component would be at 11.730 THz if the non-analytic q -> 0 term were included, which the q = Gamma kernel
calculation does not). Each component has two equal non-zero tensor entries, as required by Td symmetry for a T2 mode
(a component polarized along y has Gamma^xz = Gamma^zx; the basis the code picks inside the degenerate triplet is
rotated by 6-11 deg. from the Cartesian one, which only redistributes weight between the xy/yz/xz pairs), |Gamma^xz| =
7.1-7.2 A^2/eV at the peak, phase ~48 deg. (e.g. 4.82 + 5.35 i on 144^3), diagonal entries < 0.1 A^2/eV (numerical
noise). Summed in quadrature over the three degenerate components the peak is 17.61 A^2/eV (192^3; 17.61 on 168^3,
17.67 on 144^3).
The 2.81 eV peak coincides with the E1 critical point of GaP (L3v -> L1c transition, 2.79 eV in PBE here); the direct
gap at Gamma (1.82 eV) gives only a weak onset (total invariant 1.5 A^2/eV at 2.0 eV), and the spectrum stays at
45-65 % of the peak between 2.9 and 4.5 eV (total 13.2 at 2.9, 11.5 at 3.0, 9.0 at 4.0, 7.8 at 4.5 eV on 192^3) before
falling to ~1.5 A^2/eV at 5-5.5 eV.

Definitions and conventions used (see NOTES.md section 2): kernel Gamma_s^ab(omega_s; omega, -omega) as implemented in
the authors' EPW kernel variant (`indabs.f90`, `lindabs = .true.`; triangle diagram (c) of the manuscript + Pi_0, which is
the scope of the code in this build, "v1"), output in A^2/eV; electronic broadening degaussw = 25 meV Gaussian (the paper's
value), occupations at T = 0 with the Fermi level mid-gap (8.40 eV), band window fsthick = 7 eV (bands from VBM-6.2 eV to
CBM+6.2 eV), photon energies 0.01-6.00 eV in 0.01 eV steps, q = Gamma only (fine q-grid 1x1x1), no scissor correction
(PBE gap 1.60 eV indirect, 1.82 eV direct), no spin-orbit coupling. Because the plain sum of magnitudes
sum_ab |Gamma^ab_s| depends on the arbitrary basis chosen inside the degenerate T2 triplet (it is 17.2, 17.3 and 14.8 for the
three modes at the peak on 144^3 and 16.1, 17.6, 16.3 on 192^3, while the Frobenius norm is 10.2 in all cases), the Frobenius norm is reported as the per-mode invariant; it is the same for all three modes and
for any rotation of the Cartesian axes. The plain sums are tabulated in `results/kernel/k192/Gamma_alphabeta_s.dat_invariants.dat` (on 192^3 they are 16.1, 17.6 and 16.3 A^2/eV).

## 2. Phonons at Gamma (DFPT, acoustic sum rule)
DFPT (ph.x, PBE, 12x12x12 k, tr2_ph = 1e-16, 2x2x2 q-mesh, dielectric tensor and Born charges at Gamma), then dynmat.x
with asr = 'crystal'. Files: `results/02_ph/ph.out`, `results/02_ph/dynmat_asr.out` (ASR only),
`results/02_ph/dynmat_asr_q100.out` (ASR + non-analytic term for q -> (1,0,0)), raw dynamical matrix `results/02_ph/gap.dyn1`.

| mode | irrep (Td) | raw DFPT (cm^-1) | with ASR (cm^-1) | with ASR (THz) | with ASR + NA term, q->(100) |
|---|---|---|---|---|---|
| 1-3 acoustic | T2 (=Gamma_15) | -4.37 | 0.00 | 0.000 | 0.00 |
| 4-6 optical | T2 (=Gamma_15), IR+Raman active | 358.10 | 358.08 | 10.7349 | TO 358.08 (x2) = 10.7349 THz, LO 391.28 = 11.7302 THz |

The three optical modes are degenerate at exactly q = Gamma (no non-analytic term), which is also what EPW uses on the
fine grid: EPW reports the mode energy 44.400 meV = 10.7358 THz for modes 4, 5, 6 (`results/kernel/k*/Gamma_alphabeta_s.dat`
headers). Dielectric constant eps_inf = 10.539, Born charges Z*(Ga) = +2.147, Z*(P) = -2.156 (`results/02_ph/ph.out`).
Experiment for comparison: TO 367 cm^-1, LO 403 cm^-1 (PBE at the given lattice constant a = 5.4516 A is ~2.5 % soft).

## 3. Wannier interpolation quality
Wannier functions: 10 functions from SCDM (`scdm_proj`, erfc entanglement, mu = 16.0 eV, sigma = 1.5 eV), bands 1-5 (Ga 3d)
excluded, outer window [-6, 24] eV, frozen window [-6, 15.5] eV (absolute energies; VBM = 7.6046 eV, CBM = 9.2019 eV),
coarse mesh 16x16x16 (4096 k), spreads 2.2-2.9 A^2 (total 26.4 A^2). Input: `inputs/05_epw/wannier_tests/epw_wan16_G_s10.in`;
W90 output `results/wannier_tests/wan16_G_s10/gap.wout`.

Comparison DFT (pw.x `bands`, `inputs/04_bands/bands.in`, 387 k-points on G-X-W-K-G-L-U-W-L-K|U-X, `results/04_bands/bands.out`)
versus EPW-interpolated bands on exactly the same k-points (`band_plot`, `filkf = kpath.txt`, `results/04_bands/band_G16.eig`),
window = the 4 valence bands + conduction bands up to CBM + 6.0 eV = 15.20 eV. Data: `results/04_bands/wanG16_band_compare.dat`
(one line per k-point and band: E_DFT, E_Wannier, difference). Statistics (`scripts/parse_bands.py`):

| set | points | RMS (meV) | max |dev| (meV) |
|---|---|---|---|
| all (VB + CB <= CBM+6 eV) | 2818 | 1.67 | 20.16 |
| valence bands (4) | 1548 | 0.31 | 1.39 |
| conduction bands <= CBM+6 eV | 1270 | 2.47 | 20.16 |

Per band (band 1 = lowest sp3 valence band; bands 5-9 = CB1-CB5): RMS 0.22, 0.16, 0.37, 0.43 | 0.64, 1.11, 2.21, 5.16,
8.00 meV; max 0.76, 0.69, 1.26, 1.39 | 2.50, 5.04, 14.0, 20.2, 13.5 meV. The largest deviations (10-20 meV) occur only
where CB4 and CB5 anticross near 15 eV (close to the top of the frozen window, 6 eV above the CBM); the bands that
carry the resonant transitions for photon energies <= 6 eV (all states below VBM + 6 eV = 13.6 eV) are reproduced to
<= 5 meV. For reference, the same comparison with the first 12x12x12 coarse mesh gave RMS 4.3 meV / max 61 meV, and the
rejected projection-based sets gave 39-126 meV (NOTES.md, `results/wannier_tests/`).

## 4. Fine k-mesh convergence of the kernel
All production runs use the same Wannier data (set G, 16^3 coarse k, 2x2x2 coarse q) and differ only in the fine k-mesh
(`inputs/05_epw/epw_kN.in`, N^3 Gamma-centred full grids, no symmetry reduction). Peak of the total invariant (quadrature
over the three T2 components; per-mode value = total / sqrt(3)), `results/kernel/mesh_convergence.dat`:

| fine mesh | k-points | peak energy (eV) | peak total (A^2/eV) | per-mode Frobenius at peak | change vs previous |
|---|---|---|---|---|---|
| 24^3 | 13 824 | 2.80 | 33.35 | 19.28 | (timing test; spiky, unconverged) |
| 48^3 | 110 592 | 2.87 | 17.42 | 10.08 | -48 % |
| 72^3 | 373 248 | 2.81 | 17.84 | 10.32 | +2.5 % |
| 96^3 | 884 736 | 2.81 | 17.39 | 10.06 | -2.5 % |
| 120^3 | 1 728 000 | 2.81 | 17.46 | 10.09 | +0.4 % |
| 144^3 | 2 985 984 | 2.81 | 17.67 | 10.22 | +1.2 % |
| 168^3 | 4 741 632 | 2.81 | 17.61 | 10.18 | -0.3 % |
| 192^3 | 7 077 888 | 2.81 | 17.61 | 10.17 | -0.02 % |

The peak position is stable at 2.81 eV from 72^3 on, and the peak height is converged to about +-1.5 % from 96^3 on
(with a 25 meV Gaussian smearing the energy spacing of the fine grid along the steepest bands is ~50 meV at 144^3, so a
residual oscillation at the percent level is expected). Away from the peak the spectrum converges more slowly at
higher photon energies (e.g. the total at 4.5 eV: 11.6, 7.0, 8.3, 7.7, 7.8 A^2/eV for 48^3 ... 144^3), which does not
affect the location or the value of the maximum. Adopted mesh: 192^3 (the reported numbers), with 144^3 and 168^3 as the convergence evidence (all three agree to 0.3 % in the peak value and exactly in the peak energy). Kernel files of every mesh:
`results/kernel/kN/Gamma_alphabeta_s.dat` (raw code output) and `..._invariants.dat` (per-mode Frobenius norm, plain sum,
and total versus photon energy).

## 5. Compute used
`jobs.log` lists every Slurm job (id, purpose, partition, cores x hours). Node-hours are counted as
(CPUs reported by sacct) x elapsed / 128; on LUMI-C sacct reports hyperthreads, i.e. 256 "CPUs" for a full 128-core node,
so this count is conservative (an upper bound, 2x the physical-core count given in brackets in `jobs.log`).
Total: **9.3 node-hours** (conservative count; 4.6 node-hours by physical cores), of the 20 node-hour budget. Breakdown: SCF+DFPT 0.06, NSCF/bands 0.04, Wannierization attempts and tests 1.2 (0.85 of it the rejected 18-function first attempt), electron-phonon coarse step 0.15, kernel meshes 24^3..192^3 7.9 (24^3: 0.01, 48^3: 0.06, 72^3: 0.17, 96^3: 0.40, 120^3: 0.75, 144^3: 1.30, 168^3: 2.06, 192^3: 3.14).

## 6. Files
- `REPORT.md` (this file), `NOTES.md` (running log and decisions), `jobs.log` (one line per Slurm job), `DONE`.
- Inputs actually used: `inputs/01_scf/scf.in`; `inputs/02_ph/ph.in`, `dynmat_asr.in`, `dynmat_asr_q100.in`, `job_scf_ph.sh`;
  `inputs/03_nscf/nscf.in` (12^3, first attempt), `nscf16.in` (16^3, production), job scripts; `inputs/04_bands/bands.in`;
  `inputs/05_epw/wannier_tests/epw_wan16_G_s10.in` (production Wannierization, SCDM) and the other tested sets;
  `inputs/05_epw/epw_elph_G16.in` (electron-phonon coarse-to-Wannier step + band interpolation on the path);
  `inputs/05_epw/epw_kN.in` + `job_epw_kN.sh` (kernel runs, N = 24, 48, 72, 96, 120, 144, 168, 192);
  Wannier90 inputs generated by EPW: `inputs/05_epw/wannier90_generated/*.win`; `inputs/05_epw/epw_wan.in` (rejected first
  attempt, 18 projections). Pseudopotentials: PseudoDojo nc-fr-04 PBE standard Ga.upf (3d in valence) and P.upf, used
  without spin-orbit.
- Outputs: `results/01_scf/scf.out`; `results/02_ph/` (ph.out, dynmat outputs, gap.dyn1); `results/04_bands/bands.out`
  (DFT bands on the path), `band_G16.eig` (EPW-interpolated bands on the same path), `wanG16_band_compare.dat`
  (the comparison data), `epw_elph_G16.out`; `results/wannier_tests/` (all Wannier sets tried: .wout, W90 band plots);
  `results/kernel/kN/` (Gamma_alphabeta_s.dat = the kernel file written by the code, Pi_0.dat, epw_kN.out);
  `results/kernel/mesh_convergence.dat`.
- Scripts: `scripts/kgen.py` (k-grids and path), `parse_bands.py`, `parse_w90bands.py`, `kernel_analysis.py`,
  `mesh_convergence.py`, `mk_kernel_job.sh`, `nodehours.sh`.
- Remote root on LUMI: `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP/` (run/, run16/, wan*/, k*/).
