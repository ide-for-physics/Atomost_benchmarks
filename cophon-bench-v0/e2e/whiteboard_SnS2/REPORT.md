# REPORT — light-induced coherent-phonon generation kernel of 1T-SnS2 (bulk, P-3m1)

Status: FINAL (2026-10-15). Every number below names the file it comes from; all files are under this folder (`run/...`).

## 1. Headline result
- **Photon energy of the largest kernel invariant in 0-6 eV: 4.08 eV** (raw maximum on the adopted 120x120x60 fine mesh;
  the A_1g kernel is a plateau 4.00-4.10 eV at 48-54 Å²/eV, and a ±0.05 eV running average puts its centre at 4.06 eV on
  every mesh from 72x72x36 on). File: `run/04_epw_b/k120x120x60/kernel_k120x120x60_peaks.txt`.
- **Value: |Γ_s| = sqrt(Σ_ab |Γ^{ab}_s|²) = 53.7 Å²/eV** (96x96x48: 53.1 at 4.10 eV; 72x72x36: 53.2 at 4.02 eV; the value
  at 4.08 eV itself is 50.7 / 51.8 / 53.7 for 72 / 96 / 120). Convention note: Σ_ab|Γ^{ab}| = 83.3 and |Σ_ab Γ^{ab}| = 83.3 at
  the same point (for A_1g all nine channels have the same phase; the non-zero ones are xx = yy = 37.8, zz = 6.2 Å²/eV).
- **Dominant mode: mode 8, A_1g (Raman-active, out-of-plane S breathing), 9.202 THz = 38.06 meV = 306.9 cm⁻¹.** The only
  other modes with a non-zero kernel are the two E_g modes (6.093 THz), maximal at 5.66 eV with 13.3 Å²/eV (a quarter of the
  A_1g value). The inversion-odd E_u and A_2u modes are zero within numerical noise (≤ 0.1 Å²/eV), as inversion symmetry
  requires for a second-order (field-squared) drive in a centrosymmetric crystal.
- Adopted fine k-mesh: 120x120x60 (864 000 points); converged against 96x96x48 and 72x72x36 (Section 5).
- Caveat on the physics content: the build computes the Raman-like triangle diagram (c) of the manuscript; the
  optically-perturbed-EPC vertex diagram (e) is marked out of scope in this version of the code (Section 5).

## 2. Structure and electronic ground state
- Structure: `structure.cif` = `structure_POSCAR`, a = 3.6743056 Å, c = 6.2288318 Å, Sn (0,0,0), S (1/3,2/3,0.2346535),
  S (2/3,1/3,0.7653465); used as given (no relaxation). pw.x input: `run/01_scf/scf.in` (ibrav 4, celldm(1) 6.94343078 bohr,
  celldm(3) 1.69524055). Space group found by pw.x: 12 symmetry operations with inversion, point group D_3d (-3m).
- Pseudopotentials: PseudoDojo nc-fr-04 PBE standard (`Sn.upf`, 14 valence e; `S.upf`, 6 valence e) used without spin-orbit
  (scalar-relativistic average, allowed by the task). ecutwfc = 80 Ry (hints: Sn normal 72 / high 84 Ry, S 52 / 64 Ry).
- SCF (`run/01_scf/scf.out`): k 12x12x6, converged in 10 iterations to 2.3e-11 Ry; total energy -201.75933377 Ry;
  band edges 5.6009 eV (VBM) and 7.1723 eV (CBM): PBE gap 1.571 eV (indirect). Pressure 24 kbar, total force 0.015 Ry/bohr
  (the given structure is not the PBE minimum; kept as given).

## 3. Gamma-point phonons (DFPT, `run/02_ph/ph.in`, `run/02_ph/ph.out`; ASR by dynmat.x `run/02_ph/dynmat.in`,
   `run/02_ph/sns2.dynmat.out`)
| mode(s) | irrep (ph.x mode symmetry, D_3d) | activity | freq. before ASR (cm-1) | with ASR 'crystal' (cm-1) | THz |
|---|---|---|---|---|---|
| 1 | A_2u (acoustic) | — | 4.81 | 0.00 | 0.000 |
| 2–3 | E_u (acoustic) | — | 6.19 | 0.00 | 0.000 |
| 4–5 | E_g | Raman | 203.31 | 203.31 | 6.0950 |
| 6–7 | E_u | IR | 208.01 | 208.08 | 6.2381 |
| 8 | A_1g | Raman | 306.94 | 306.94 | 9.2019 |
| 9 | A_2u | IR | 340.49 | 340.55 | 10.2094 |
Dielectric tensor (ph.x, epsil): eps_inf = 7.874 (xx = yy), 4.675 (zz). Born charges (ASR applied): Z*(Sn) = 4.923 (xx,yy),
1.503 (zz); Z*(S) = -2.461, -0.751. (`run/02_ph/ph.out`). The IR-active modes are quoted at their TO frequencies
(q = 0 exactly, no non-analytic term), which is what enters the kernel code.

## 4. Wannier interpolation quality
Setup (`run/04_epw/epw1.in`, Wannier90 driven by EPW; log `run/04_epw/sns2.wout`): 17 Wannier functions from projections
Sn s,p,d + S s,p on the 12x12x6 coarse grid, bands 1-5 (Sn 4d semicore, -15.3..-15.1 eV) excluded, outer window
[-9, 24] eV, frozen window [-9, 13.5] eV (CBM + 6.3 eV; band 19 starts at 13.58 eV so at most 13 non-semicore bands are
frozen at any k; `scripts/parse_pw_eigs.py run/03_nscf/nscf.out --count 13.5`). Spreads: Omega_I 29.76, Omega_D 0.26,
Omega_OD 7.61, total 37.64 Å² (1.50-3.68 Å² per function).
Comparison DFT vs Wannier along Γ-M-K-Γ-A-L-H-A, 360 k-points (DFT: `run/05_bands/bands.in`/`bands.out`, parsed into
`run/05_bands/dft_bands_path.txt`; Wannier: `run/04_epw/sns2_band.dat` on the same points `sns2_band.kpt`; script
`scripts/compare_bands.py`, nearest-band matching; table in `run/05_bands/wannier_vs_dft_v1.txt`):

| energy window (eV, absolute; VBM = 5.60, CBM = 7.17) | RMS (meV) | max (meV) |
|---|---|---|
| [-9, 13.2] = all valence (S 3s + S 3p) + conduction up to CBM + 6.0 eV | 1.38 | 28.2 (at 13.19 eV) |
| [-9, 8.7] = valence + first conduction band | 0.26 | 1.09 |
| [-9, -5] S 3s | 0.17 | 0.75 |
| [-5, 0] | 0.16 | 0.52 |
| [0, 6] upper valence | 0.28 | 1.09 |
| [6, 9] | 0.35 | 1.06 |
| [9, 11] | 0.52 | 2.17 |
| [11, 12] | 1.35 | 5.76 |
| [12, 12.5] | 1.59 | 5.93 |
| [12.5, 13.0] | 3.35 | 12.2 |
| [13.0, 13.2] | 7.54 | 28.2 |

The interpolation is sub-meV through the valence bands and the first conduction band, a few meV up to 12.5 eV
(CBM + 5.3 eV), and degrades only in the last 0.7 eV below the frozen-window top (13.5 eV), where the 17th Wannier band is
built from the least localized states. Two attempts to push the frozen window higher (14.3 eV, `run/04_epw_v2`; 13.9 eV,
`run/04_epw_v3`) are documented in NOTES.md: the 14.3 eV one delocalized the functions (total spread 59 Å²) and ruined
the bands (RMS 36 meV, `run/05_bands/wannier_vs_dft_v2.txt`) and was rejected; the 13.9 eV one (v3, default mixing)
did the same (total spread 57.6 Å², RMS 67 meV, `run/05_bands/wannier_vs_dft_v3.txt`) and was rejected too. The v1
functions above are therefore the final ones; all kernel results in Section 5 use them.
For the kernel in the 0-6 eV photon-energy range only states below VBM + 6 eV = 11.6 eV can be resonant; there the
interpolation error is at most 5.8 meV (RMS 1.3 meV).
The real-space decay of the Wannier Hamiltonian (`run/04_epw/decay.H`) drops from 1 Ry on site to 2e-4 Ry at 17 Å; the
e-ph matrix elements (`decay.epmate`) decay from 0.54 to 6e-4 Ry over the same distance.

## 5. Kernel: fine-mesh convergence and result
Code path: the authors' kernel variant computes, in `indabs_main` (EPW/src/indabs.f90 of qe-phnlo-75), the second-order
kernel Γ^{ab}_s(ω_s; ω, -ω) from the triangle diagram (c) of the manuscript (the vertex diagram (e) with g^{s;α} is marked
"out of scope in v1" in the source and is not computed by this build), with a Gaussian δ(ħω - ε_nm) of width `degaussw`
and the phonon-resonant denominator 1/(ħω_s + ε_ln + i·degaussw). Output `Gamma_alphabeta_s.dat`: Re/Im of the nine
Cartesian channels in Å²/eV per optical mode. Settings (`run/04_epw/epw1.in` and the `epw_k*.in` files): photon energies
0.02-6.00 eV in steps of 0.02 eV (the formula carries 1/ω², so the grid starts one step above 0), degaussw = 0.025 eV
(as in the paper), Fermi level 6.40 eV (mid-gap), fsthick 12 eV (all 17 Wannier bands enter), T = 300 K (unused by the
kernel), fine q-mesh = Γ only, coarse q-mesh = Γ only (DFPT at Γ; the q-Fourier transform with one lattice vector is
exact), lpolar = .false. (irrelevant at q = Γ), velocities from the Wannier Hamiltonian (vme = 'wannier').

Invariant: for a rank-2 tensor the rotation-invariant magnitude built from the Cartesian channels is the Frobenius
norm |Γ_s|(ω) = sqrt(Σ_ab |Γ^{ab}_s(ω)|²); this is what is tabulated (`scripts/kernel_invariants.py`, files
`kernel_*_invariants.dat` next to each `Gamma_alphabeta_s.dat`). The same files also give Σ_ab|Γ^{ab}| and |Σ_ab Γ^{ab}|
(isotropic-field combination used in the SI amplitude formula) for readers who prefer those conventions.

Fine-mesh series with the final (v1) Wannier functions (`run/04_epw/convergence_v1.txt`, meshes in the ratio a*:c* ≈ 2:1):

| fine k-mesh | k-points | A_1g (mode 8): photon energy of max / max of \|Γ\| (Å²/eV) | E_g (modes 4,5): max | run |
|---|---|---|---|---|
| 24x24x12 | 8 064 | 4.04 / 73.4 | 5.90 / 14.4, 14.2 | `run/04_epw/k24x24x12` |
| 36x36x18 | 23 328 | 3.94 / 58.1 | 5.66 / 13.3, 13.2 | `run/04_epw/k36x36x18` |
| 48x48x24 | 55 296 | 4.06 / 56.1 | 5.66 / 13.0, 12.8 | `run/04_epw/k48x48x24` |
| 60x60x30 | 108 000 | 4.08 / 57.1 | 6.00 / 13.2, 13.1 | `run/04_epw/k60x60x30` |
| 72x72x36 | 186 624 | 4.02 / 53.2 | 5.66 / 13.4, 13.2 | `run/04_epw_b/k72x72x36` |
| 96x96x48 | 442 368 | 4.10 / 53.1 | 5.64-5.66 / 13.3, 13.1 | `run/04_epw_b/k96x96x48` |
| 120x120x60 | 864 000 | 4.08 / 53.7 | 5.66 / 13.3, 13.1 | `run/04_epw_b/k120x120x60` (adopted) |

The A_1g kernel has a broad maximum (plateau 3.9-4.2 eV, 44-54 Å²/eV; on 120x120x60 the values at 4.00, 4.02, ...,
4.12 eV are 48.6, 50.3, 50.6, 51.7, 53.7, 52.4, 48.8). The maximum value changes by 1.2 % from 96 to 120 and by 1.0 %
from 72 to 120; point by point the three finest meshes agree within 1-5 % on the plateau (`convergence_v1.txt`, second
table), the residual noise of a 25 meV Gaussian on these meshes. The photon energy of the raw maximum wanders inside the
plateau (4.02 / 4.10 / 4.08 eV for 72 / 96 / 120); a ±0.05 eV running average (`scripts/smoothed_peak.py`,
`run/04_epw/smoothed_peaks_v1.txt`) gives 4.04 / 4.06 / 4.06 eV with smoothed heights 51.6 / 51.7 / 51.8 Å²/eV, and a
±0.10 eV average gives 4.08 / 4.04 / 4.06 eV at 49.8 / 49.8 / 49.6. The E_g maxima are at 5.66 eV on every mesh from
36x36x18 on with values stable to 0.5 % (13.37 / 13.27 / 13.29). The inversion-odd modes (E_u, A_2u) give 0.04-0.10 Å²/eV
on all meshes, i.e. zero within numerical noise, as required by inversion symmetry for a second-order (E·E, even) drive.
Adopted mesh: 120x120x60; quoted uncertainty from the mesh: ±1 Å²/eV on the value, ±0.04 eV on the position.

Per-mode result on the adopted 120x120x60 mesh (`run/04_epw_b/k120x120x60/kernel_k120x120x60_peaks.txt`; the
mode indices are EPW's, 1-3 acoustic):

| mode | irrep | ħω_s (meV) | THz | photon energy of max (eV) | max \|Γ\| = sqrt(Σ\|Γ_ab\|²) | Σ\|Γ_ab\| | \|ΣΓ_ab\| | largest channels (Å²/eV) |
|---|---|---|---|---|---|---|---|---|
| 4 | E_g | 25.199 | 6.0930 | 5.66 | 13.29 | 31.65 | 5.78 | yz 7.4, zy 7.3, xz 5.6 |
| 5 | E_g | 25.199 | 6.0930 | 5.66 | 13.15 | 31.27 | 22.94 | xz 7.4, zx 7.2, yz 5.5 |
| 6 | E_u | 25.781 | 6.2337 | (4.10) | 0.04 | 0.11 | 0.01 | — (zero) |
| 7 | E_u | 25.781 | 6.2337 | (4.08) | 0.10 | 0.23 | 0.03 | — (zero) |
| 8 | A_1g | 38.057 | 9.2021 | **4.08** | **53.74** | 83.29 | 83.28 | xx 37.8, yy 37.7, zz 6.2 |
| 9 | A_2u | 42.214 | 10.2073 | (5.30) | 0.05 | 0.11 | 0.03 | — (zero) |

(EPW's Γ-point energies agree with the DFPT+ASR ones of Section 3 to < 0.1 cm⁻¹. For the E_g pair the weight sits in the
xz/yz/yy channels, consistent with the D_3d Raman tensors, which is why the Frobenius norm, not a single channel, is the
right per-mode measure.)

Raw kernel files written by the code (each with its `Pi_0.dat` companion and the derived `kernel_*_invariants.dat` /
`kernel_*_peaks.txt`): `run/04_epw/k24x24x12`, `k36x36x18`, `k48x48x24`, `k60x60x30`; `run/04_epw_b/k72x72x36`,
`k96x96x48`, `k120x120x60`. Rejected Wannier variants: `run/04_epw_v2/k48x48x24` (and 72/96, not copied),
`run/04_epw_v3/k48x48x24`.

## 6. Compute used
`jobs.log` lists every Slurm job (id, purpose, partition, allocation x hours). Full-node (`standard`) jobs: 0.661 + 1.105 +
0.862 = 2.63 node-hours. Shared (`small`/`debug`) jobs: 2.09 node-hours when counted with the allocated hardware threads
(Slurm's AllocCPUS = 2 per physical core on LUMI-C), which is the conservative number; counted per physical core it is 1.05.
**Total: 4.72 node-hours (conservative) / 3.67 (per-core), of the 20 allowed.** 1.1 of these went to the rejected
Wannier variant v2 (its 72/96 meshes and a cancelled 120 run) and 0.77 to the rejected v3; the adopted chain
(SCF, DFPT, NSCF, Wannierization, 7 meshes, bands) cost 2.2 node-hours.

## 7. Inputs and files delivered
- pw.x: `run/01_scf/scf.in`, `run/03_nscf/nscf.in` (explicit 864-point list, `nosym`/`noinv`), `run/05_bands/bands.in`.
- ph.x / dynmat.x: `run/02_ph/ph.in`, `run/02_ph/dynmat.in`; outputs `ph.out`, `dynmat.out`, `sns2.dynmat.out`,
  `sns2.dynmat.eig`, `sns2.dyn1`.
- Wannier90 (generated by EPW from `epw1.in`): `run/04_epw/sns2.win`; log `sns2.wout`; centres `sns2_centres.xyz`;
  interpolated bands `sns2_band.dat` on `sns2_band.kpt`.
- epw.x: `run/04_epw/epw1.in` (Wannierize + 24x24x12), `run/04_epw/epw_k36x36x18.in`, `epw_k48x48x24.in`,
  `epw_k60x60x30.in`, `run/04_epw_b/epw_k72x72x36.in`, `epw_k96x96x48.in`, `epw_k120x120x60.in` (the last three read the
  stored Wannier-basis matrix elements, `epwread`); outputs `epw1.out`, `epw_k*.out`.
- Wannier-vs-DFT comparison: `run/05_bands/dft_bands_path.txt` (DFT, 360 k x 40 bands), `run/04_epw/sns2_band.dat`,
  `run/05_bands/wannier_vs_dft_v1.txt` (final), `_v2.txt`, `_v3.txt` (rejected variants).
- Job scripts: `run/*/job_*.sh`. Analysis scripts: `scripts/`. Logs: `jobs.log`, `NOTES.md`, `DECISION.log`, `RUNNING.log`.
- Remote root on LUMI (2.2 GB after clean-up; wavefunctions and coarse e-ph files deleted):
  `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/SnS2/`.

## 8. Assumptions and limitations (stated, not hidden)
- The code computes diagram (c) only ("Gamma_c triangle ... Gamma_e / Pi_kernel out of scope in v1", EPW/src/indabs.f90).
- No spin-orbit coupling (PseudoDojo fully relativistic files used scalar-relativistically); PBE; the given cell was not
  relaxed (24 kbar residual pressure).
- The δ-function width 25 meV with a 120x120x60 mesh leaves a residual point-to-point scatter of a few % on the A_1g
  plateau; the peak position is therefore quoted with ±0.04 eV.
- "Rotational invariant" is taken as the Frobenius norm over the nine Cartesian channels; the two other sums are given
  alongside so the number can be re-expressed in either convention.

