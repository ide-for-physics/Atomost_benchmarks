# NbFeSb (mp-9437): second-order light-induced coherent-phonon generation kernel

Material: half-Heusler NbFeSb, sealed fcc cell (space group F-43m, point group Td), 3 atoms, 9 phonon modes.
Code: Quantum ESPRESSO 7.5 + the authors' modified EPW ("kernel variant", `lindabs` branch of `indabs.f90`) on LUMI-C.
All numbers below are traceable to files in this folder (`kernel/`, `wannier/`, `remote_out/`, `inputs/`, `jobs.log`).

## 1. Headline numbers (= RESULT.json)

| quantity | value | source |
|---|---|---|
| converged fine k-mesh | 96x96x96 (full BZ, nqf = Gamma only) | `inputs/epw/epw_kern96.in` |
| photon energy of the largest invariant (0-6 eV) | 3.35 eV | `kernel/Gamma_alphabeta_s.dat` |
| its value, I_s = sum over the 9 Cartesian channels of abs(Gamma^{ab}_s) | 29.011 A^2/eV | same |
| dominating mode | mode 8 of the upper T2 triplet, 34.116 meV = 8.2492 THz (EPW at Gamma); DFPT+ASR 275.40 cm-1 = 8.2564 THz | `remote_out/phband.freq`, `remote_out/dynmat.out` |
| irrep | T2 (Td), IR + Raman active | `remote_out/ph.out` |
| compute | 4.47 node-hours (14 Slurm jobs) | `jobs.log` |

Invariant definition used: for each mode s and photon energy w, I_s(w) = sum_{a,b in x,y,z} |Gamma^{ab}_s(w_s; w, -w)|
(per-mode magnitudes summed over the Cartesian channels). The Frobenius norm F_s = sqrt(sum |Gamma^{ab}|^2) peaks at the
same energy; both are tabulated in section 6. Inside a degenerate T2 triplet the split between the three partner modes is
set by the (arbitrary) basis chosen by the dynamical-matrix diagonalizer; the triplet sums are basis independent.

## 2. Structure and ground state

- Cell used exactly as given: a1 = (0, 2.9468919, 2.9468919) A, a2 = (2.9468919, 0, 2.9468919) A, a3 = (2.9468919, 2.9468919, 0) A
  (conventional a = 5.8937838 A); Nb (0,0,0), Fe (1/4,1/4,1/4), Sb (1/2,1/2,1/2) crystal. No cell relaxation.
  Internal coordinates are fixed by symmetry (Wyckoff 4a/4c/4b); the SCF forces are exactly zero, so no internal
  relaxation was needed. Residual pressure in the sealed cell: +62.6 kbar (PBE).
- PBE, PseudoDojo nc-fr-04 standard (Nb 13e, Fe 16e, Sb 15e), used scalar-relativistically (no SOC), ecutwfc 90 Ry,
  ecutrho 360 Ry, 12x12x12 k, fixed occupations, conv_thr 1e-10. E = -557.11805314 Ry.
- Band gap (PBE, 12^3 mesh): VBM 16.9722 eV, CBM 17.5050 eV, Eg = 0.533 eV (indirect). The Fermi level used in EPW is
  mid-gap, 17.24 eV.
- Inputs: `inputs/scf/scf.in`, `inputs/nscf/nscf.in` (8x8x8 uniform grid in [0,1), nosym, 44 bands),
  `inputs/bands/bands.in` (242-point path G-X-W-K-G-L-U-W-L-K).

## 3. DFPT phonons at Gamma (acoustic sum rule applied)

ph.x at q = Gamma (ldisp 1x1x1, tr2_ph 1e-16, epsil = .true.), `inputs/ph/ph.in`; then dynmat.x with asr = 'crystal'
(`inputs/ph/dynmat.in`, output `remote_out/dynmat.out`):

| modes | freq (cm-1) | freq (THz) | freq (meV) | irrep (ph.x) | IR activity ((D/A)^2/amu) |
|---|---|---|---|---|---|
| 1-3 | 0.00 (raw ph.x: 7.0) | 0 | 0 | T2 acoustic | 0 |
| 4-6 | 214.54 | 6.4319 | 26.60 | T2, I+R | 1.53 |
| 7-9 | 275.40 | 8.2564 | 34.15 | T2, I+R | 30.05 |

Dielectric tensor eps_inf = 24.01 (isotropic); Born charges Z*(Nb) = +5.028, Z*(Fe) = -7.625, Z*(Sb) = +2.597 (sum 0).
EPW's interpolated frequencies at Gamma (its own sum rule, `remote_out/phband.freq`): 0, 26.5995 meV (6.4317 THz),
34.1159 meV (8.2492 THz); the 0.1% difference to dynmat.x comes from the different ASR implementation.

## 4. Wannier interpolation quality

- 19 Wannier functions (Nb s,p,d; Fe s,d; Sb s,p), 13 semicore bands excluded (Fe 3s3p, Nb 4s4p, Sb 4d, all below
  -11.7 eV), outer window 0-38 eV, frozen window 2.0-24.0 eV (CBM + 6.5 eV), coarse 8x8x8 grid, EPW-internal
  wannier90 (`inputs/epw/epw_wan.in`, generated `inputs/epw/nfs.win`). Total spread 28.29 A^2 (Omega_I 23.89), individual
  spreads 0.62-2.44 A^2 (`wannier/wannier_spreads.txt`).
- DFT vs Wannier on the identical 242-point path (`wannier/dft_bands_path.dat`, `wannier/epw_band.eig`,
  `wannier/band_comparison.txt`, per-k differences in `wannier/band_diff_meV.dat`):

| window | points | RMS (meV) | max abs (meV) |
|---|---|---|---|
| valence bands 14-22 (Sb 5s + 8 upper valence) | 2178 | 1.29 | 6.55 |
| conduction bands, CBM to CBM + 6 eV | 1460 | 6.33 | 55.1 |
| both | 3638 | 4.13 | 55.1 |

The largest deviations are confined to the top 0.5 eV of the conduction window (bands 28-29 near 23.5 eV, the
free-electron-like region just below the frozen-window edge); bands up to CBM + 4 eV agree to <= 6 meV RMS per band.

## 5. Kernel calculation set-up

- EPW: `elph`, `vme = 'wannier'` (h^a = dH/dk + i eps r, as in the implementation note), `lpolar` with eps_inf and Z*,
  `lindabs = .true.`, photon grid 0.01-6.00 eV in 0.01 eV steps, degaussw = 0.025 eV (the paper's electronic broadening),
  fsthick = 100 eV (all 19 bands enter), eps_acoustic = 5 cm-1, efermi_read (17.24 eV), T = 300 K, nqf = 1x1x1 (Gamma),
  nkf = N^3 full grid, npool = number of MPI ranks. Inputs `inputs/epw/epw_kernN.in`.
- The code evaluates the triangle diagram (c) of the manuscript (Eq. 5 / SI Eq. for Gamma|_c) with Gaussian deltas and
  writes `Gamma_alphabeta_s.dat` in A^2/eV for modes 4-9 (columns: w, Re/Im xx, yy, zz, xy, xz, yz, yx, zx, zy).
- Symmetry check (Td): the tensor is symmetric (xy = yx, xz = zx, yz = zy to 0.3%), the diagonal channels are
  mesh noise (< 2% of the off-diagonal maxima at 96^3), i.e. only the xyz-type invariant survives, as it must.

## 6. Mesh convergence

Peak of I_s(w) = sum_ab |Gamma^ab_s| in 0-6 eV (A^2/eV) and its position:

| mode (meV) | 24^3 | 48^3 | 72^3 | 96^3 |
|---|---|---|---|---|
| 4 (26.60) | 15.988 @ 3.37 | 15.304 @ 3.35 | 15.376 @ 3.35 | 15.376 @ 3.35 |
| 5 (26.60) | 15.163 @ 3.37 | 14.550 @ 3.35 | 14.616 @ 3.35 | 14.617 @ 3.35 |
| 6 (26.60) | 19.312 @ 3.37 | 18.465 @ 3.35 | 18.558 @ 3.36 | 18.555 @ 3.35 |
| 7 (34.12) | 24.236 @ 3.37 | 24.058 @ 3.35 | 24.169 @ 3.35 | 24.112 @ 3.35 |
| 8 (34.12) | 29.091 @ 3.37 | 28.942 @ 3.35 | 29.076 @ 3.35 | **29.011 @ 3.35** |
| 9 (34.12) | 26.055 @ 3.37 | 26.231 @ 3.35 | 26.325 @ 3.35 | 26.268 @ 3.35 |

Relative change of the dominant-mode (mode 8) peak: 24->48: -0.5%, 48->72: +0.5%, 72->96: -0.2%; the peak position is 3.35 eV on every mesh >= 48^3. Maximum deviation of the
full I_s(w) spectrum (0.01 eV grid) relative to the 96^3 run: 48^3: 1.3-2.6%, 72^3: 0.7-1.3% of the peak (mode dependent); the kernel is converged to well below 1% at 96^3. The 96^3 kernel is the
delivered `kernel/Gamma_alphabeta_s.dat`; the coarser ones are kept as `kernel/Gamma_alphabeta_s_<mesh>.dat`.

Triplet-summed Frobenius norms (basis independent): lower T2 triplet (modes 4-6): 12.93 A^2/eV at 3.35 eV; upper T2 triplet (modes 7-9): 20.40 A^2/eV at 3.35 eV (sum of the three per-mode I_s: 48.55 and 79.39 A^2/eV). Secondary maxima of the upper triplet: 3.22 eV (10.1), 1.86 eV (5.5), 1.77 eV (5.2), 1.99 eV (3.9), 2.96 eV (3.6) A^2/eV; the kernel vanishes below ~1.4 eV (direct transitions only start well above the 0.53 eV indirect gap).

## 7. Compute

4.47 node-hours in total (see `jobs.log`): the kernel runs dominate (24^3 0.04, 48^3 0.34, 72^3 1.18, 96^3 2.62 nh);
DFT/DFPT/Wannier steps together < 0.3 nh. Wall-clock from session start to DONE: 3.7 h.
