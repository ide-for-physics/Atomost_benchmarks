# REPORT — light-induced coherent-phonon generation kernel of InPS4 (mp-20790, sealed cell)

cophon-bench v1, whiteboard arm, model fable. All numbers below are traceable to files in this folder
(`kernel/`, `wannier/`, `phonons/`, `pulled/`, `inputs/`, `jobs.log`); analysis scripts are in `scripts/`.

## 1. Result (RESULT.json)

| quantity | value | source |
|---|---|---|
| peak photon energy | **3.10 eV** | `kernel/Gamma_alphabeta_s.dat` (96³), `scripts/analyze_kernel.py` |
| peak invariant S1 = Σ_ab \|Γ^{ab}_s\| | **114.74 Å²/eV** (96³; 72³: 114.78, 48³: 114.19) | same |
| dominating mode | mode 11, **7.871 THz** (32.553 meV, 262.56 cm⁻¹), irrep **A** (point group S4) | kernel file header; `phonons/gamma_mode_symmetry_phx.txt` |
| adopted fine k-mesh | **96×96×96** (coarse 6×6×6 k, q = Γ only) | `inputs/epw_kernel_96.in` |
| compute | 8.59 node-hours (of 20), see `jobs.log` | `jobs.log` |

Definition of the invariant. The code writes the complex tensor Γ^{ab}_s(ω_s; ω, −ω) (Å²/eV) for the nine Cartesian
channels xx, yy, zz, xy, xz, yz, yx, zx, zy, for every optical mode s = 4..18, on a photon-energy grid
ω = 0, 0.05, …, 6.00 eV. Per mode and photon energy I form S1_s(ω) = Σ_{ab} |Γ^{ab}_s(ω)| (the per-mode magnitudes
summed over the Cartesian channels) and search its maximum over 0 < ω ≤ 6 eV and over modes. The ω = 0 row is NaN
in the code output (1/ω² prefactor) and is skipped. The strictly rotation-invariant Frobenius norm
‖Γ_s‖ = (Σ_{ab}|Γ^{ab}_s|²)^{1/2} peaks at the same energy and mode (96³: 61.64 Å²/eV) and is listed as a cross-check.

## 2. Structure and electronic ground state

Sealed cell (structure.cif = structure_POSCAR), used exactly (Å):
```
 -2.82951505  2.82951505  4.48412705
  2.82951505 -2.82951505  4.48412705
  2.82951505  2.82951505 -4.48412705
```
Species In, P, S, S, S, S at the crystal coordinates of structure_POSCAR (RESULT.json `positions_crystal`).
Space group I-4 (No. 82), point group S4; pw.x finds 4 symmetry operations, no inversion.
Internal coordinates were not relaxed: at the given positions the PBE forces are ≤ 3.4·10⁻⁵ Ry/bohr
(total force 9.8·10⁻⁵, `pulled/scf/scf.out`), i.e. the structure is already relaxed for this cell.

pw.x (QE 7.5 of the toolchain), PBE, PseudoDojo nc-fr-04 standard pseudopotentials for In, P, S used
scalar-relativistically (no spin–orbit), ecutwfc = 80 Ry, ecutrho = 320 Ry, 6×6×6 k-grid, conv_thr 1e-12,
diago_thr_init 5e-6 (build quirk). Total energy −235.13538538 Ry, pressure 18.9 kbar (cell sealed).
Band gap (PBE): VBM 4.5773 eV, CBM 6.8554 eV at Γ, gap 2.278 eV; mid-gap 5.7164 eV is used as the Fermi level in EPW.
42 valence electrons (In 4d¹⁰5s²5p¹, P 3s²3p³, S 3s²3p⁴), 21 occupied bands, 40 bands computed.

Inputs: `inputs/pw_scf.in`, `inputs/pw_nscf.in` (216 explicit k-points of the full 6×6×6 grid in [0,1), nosym),
`inputs/pw_bands.in` (83 k-points on the closed path (0,0,0)→(½,0,0)→(½,½,0)→(0,½,0)→(0,0,0)→(0,0,½)→(½,0,½)→
(½,½,½)→(0,½,½)→(0,0,½) in reduced coordinates of the primitive (body-centred tetragonal) reciprocal lattice,
step 0.05, `inputs/path.dat`).

## 3. Phonons at Γ (DFPT, acoustic sum rule)

ph.x (`inputs/ph_q.in`, tr2_ph = 1e-16, 3×3×3 q-grid including Γ, dvscf written; only q = Γ enters the kernel).
Dielectric tensor ε∞ = diag(5.787, 5.787, 6.114); Born charges (ASR applied) In 3.02, P 2.86, S −1.47 (mean Z*).
Acoustic sum rule imposed with dynmat.x (`asr = 'crystal'`, `phonons/dynmat_gamma.out`, `phonons/dynmat.out`):
‖dyn(ASR) − dyn‖ = 2.6·10⁻⁴, acoustic modes 4.4/5.1/5.1 cm⁻¹ → 0.00 cm⁻¹.

| mode | irrep (ph.x, S4) | DFPT raw (cm⁻¹) | ASR (cm⁻¹) | ASR (THz) | EPW mode energy used in kernel (meV / cm⁻¹) | IR act. (D/Å)²/amu |
|---|---|---|---|---|---|---|
| 1–3 | B, E, E* (acoustic) | 4.44, 5.15, 5.15 | 0.00 | 0.000 | — | — |
| 4, 5 | E | 83.857 | 83.89 | 2.5148 | 10.380 / 83.72 | 0.59 |
| 6 | B | 109.900 | 109.93 | 3.2956 | 13.616 / 109.82 | 3.21 |
| 7 | A | 147.548 | 147.55 | 4.4234 | 18.286 / 147.49 | 0.00 |
| 8, 9 | E | 169.465 | 169.48 | 5.0808 | 21.002 / 169.39 | 0.95 |
| 10 | B | 244.902 | 244.90 | 7.3419 | 30.358 / 244.86 | 0.14 |
| 11 | A | 262.630 | 262.63 | 7.8734 | 32.553 / 262.56 | 0.00 |
| 12 | B | 310.615 | 310.61 | 9.3118 | 38.504 / 310.55 | 3.49 |
| 13, 14 | E | 319.107 | 319.10 | 9.5665 | 39.556 / 319.04 | 3.94 |
| 15 | A | 398.796 | 398.80 | 11.9556 | 49.440 / 398.76 | 0.00 |
| 16 | B | 500.377 | 500.38 | 15.0009 | 62.036 / 500.36 | 11.01 |
| 17, 18 | E | 537.651 | 537.65 | 16.1184 | 66.658 / 537.63 | 9.84 |

EPW applies its own ASR to the Γ dynamical matrix before interpolation; the mode energies it writes into the kernel
file agree with dynmat.x within 0.1 cm⁻¹ (the small offset is the ASR variant). Mode 11 (A, 262.6 cm⁻¹) is the
fully symmetric In–S/P–S breathing-type mode that dominates the kernel.

## 4. Wannier interpolation quality

EPW Wannierization (inputs in `inputs/epw_kernel_*.in`; generated `inputs/inps4_epw_generated.win`): 24 Wannier
functions from s and p projections on all six atoms, disentanglement window [−4.5, 15.0] eV, frozen window
[−1.0, 12.9] eV (absolute energies; VBM = 4.58 eV, CBM = 6.86 eV). The manifold contains the 12 valence bands
above −4.5 eV (the P-3s-derived band at −4.1 eV and the 11 S-3p/In/P bands between −0.6 and 4.6 eV) and the lowest
conduction bands; the In-4d and S-3s bands (−10.7 … −6.9 eV) are excluded. Final spread 98.37 Å² (Ω_I 73.77,
Ω_D 0.52, Ω_OD 24.07); identical in the 48³, 72³ and 96³ runs, which re-do the deterministic Wannierization.

Comparison with DFT (pw.x bands) along the 83-point path of Sec. 2 (`scripts/analyze_bands.py`; Wannier
bands from `inps4_hr.dat` + `inps4_wsvec.dat`, use_ws_distance; data: `wannier/inps4_dft.dat`,
`wannier/inps4_wan.dat`, per-band deviations `wannier/inps4_compare.dat`; each Wannier band is matched to the
nearest DFT eigenvalue):

| set of bands | N (bands × k) | RMS deviation | max \|deviation\| |
|---|---|---|---|
| valence bands in the manifold (12 bands) | 996 | **1.37 meV** | 6.9 meV |
| conduction bands up to CBM + 3 eV | 416 | 2.30 meV | 11.6 meV |
| conduction bands up to CBM + 4.5 eV | 602 | 3.14 meV | 19.2 meV |
| conduction bands up to CBM + 6 eV | 822 | 8.11 meV | 63.0 meV |
| valence + conduction to CBM + 6 eV | 1818 | 5.55 meV | 63.0 meV |

The largest deviations (40–63 meV) all occur at 12.3–12.8 eV, the top edge of the frozen window where the Wannier
manifold starts to disentangle from higher bands. For photon energies ≤ 6 eV the resonant conduction states lie
below VBM + 6 eV = 10.6 eV (= CBM + 3.8 eV), where the interpolation error is 2–3 meV RMS, i.e. within a few meV
as required.

## 5. Kernel calculation (modified EPW, "kernel variant")

`inputs/epw_kernel_{48,72,96}.in`: elph, Wannierization as above, coarse 6×6×6 k and 1×1×1 q (Γ), fine
nkf = 48³/72³/96³, nqf = 1×1×1, `lindabs = .true.` switches on the kernel in `indabs.f90` (triangle diagram
Γ_c with the interpolated g^s_{mn} and velocity matrix elements h^α_{mn}), photon grid `omegamin = 0`,
`omegamax = 6`, `omegastep = 0.05` eV, broadening `degaussw = 0.025 eV` (fixed, `ladsmear = .false.`, as in the
paper's SI), `efermi_read` with Ef = 5.7164 eV (mid-gap), T = 300 K (occupations are step functions for this
gapped system), all 24 Wannier bands included. Output `Gamma_alphabeta_s.dat` (Å²/eV) and `Pi_0.dat`.
Each run: npool = number of MPI ranks (128 per node), `srun -n <ranks> epw.x -nk <ranks>` (`jobs/epw_kernel_job*.sh`).

### Mesh convergence

Largest invariant (mode 11, A, 32.553 meV, at 3.10 eV):

| fine mesh | S1 = Σ\|Γ^{ab}\| (Å²/eV) | change vs previous | Frobenius (Å²/eV) | file |
|---|---|---|---|---|
| 48×48×48 | 114.191 | — | 61.353 | `kernel/Gamma_alphabeta_s_48x48x48.dat` |
| 72×72×72 | 114.777 | +0.51 % | 61.662 | `kernel/Gamma_alphabeta_s_72x72x72.dat` |
| 96×96×96 (adopted) | **114.737** | −0.035 % | 61.639 | `kernel/Gamma_alphabeta_s.dat` (= `_96x96x96.dat`) |

The peak position (3.10 eV on the 0.05 eV photon grid) and the dominating mode are the same on all three meshes;
the peak value changes by 0.5 % from 48³ to 72³ and by 0.04 % from 72³ to 96³, i.e. it is converged to well below
1 % on the adopted 96³ mesh. Spectrum of mode 11 at selected photon energies (S1, Å²/eV); 72³ → 96³ changes are
≤ 0.1 % at every point:

| ω (eV) | 2.25 | 2.50 | 2.75 | 3.00 | 3.25 | 3.50 | 3.75 | 4.00 | 4.50 | 5.00 | 5.50 | 6.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 48³ | 1e-25 | 3.890 | 11.500 | 79.10 | 77.01 | 46.57 | 63.73 | 58.27 | 83.07 | 52.48 | 34.23 | 39.19 |
| 72³ | 8e-26 | 3.917 | 11.378 | 79.35 | 76.58 | 46.42 | 63.93 | 58.44 | 82.89 | 52.56 | 34.25 | 39.16 |
| 96³ | 7e-26 | 3.918 | 11.376 | 79.26 | 76.53 | 46.47 | 63.94 | 58.43 | 82.82 | 52.52 | 34.26 | 39.17 |

The kernel is zero below the PBE gap (2.28 eV), as it must be for the purely electronic resonance. The per-mode
maxima of all 15 optical modes agree between 72³ and 96³ to better than 0.1 % (0.7 % for the small B mode 6).

### Per-mode overview (96×96×96)

| mode | irrep | ω (meV) | ω (THz) | S1 at 3.10 eV | S1 max | at ω (eV) |
|---|---|---|---|---|---|---|
| 4 | E | 10.380 | 2.510 | 5.55 | 10.84 | 3.30 |
| 5 | E | 10.384 | 2.511 | 6.10 | 11.43 | 3.30 |
| 6 | B | 13.616 | 3.292 | 2.68 | 10.46 | 5.50 |
| 7 | A | 18.286 | 4.422 | 83.98 | 84.00 | 3.05 |
| 8 | E | 21.002 | 5.078 | 4.41 | 7.31 | 4.50 |
| 9 | E | 21.005 | 5.079 | 4.85 | 7.42 | 4.50 |
| 10 | B | 30.358 | 7.341 | 6.51 | 8.69 | 5.60 |
| **11** | **A** | **32.553** | **7.871** | **114.74** | **114.74** | **3.10** |
| 12 | B | 38.504 | 9.310 | 1.73 | 11.74 | 4.50 |
| 13 | E | 39.556 | 9.565 | 3.19 | 7.78 | 4.50 |
| 14 | E | 39.558 | 9.565 | 2.88 | 7.56 | 4.40 |
| 15 | A | 49.440 | 11.955 | 8.04 | 66.30 | 5.25 |
| 16 | B | 62.036 | 15.000 | 2.67 | 10.93 | 5.25 |
| 17 | E | 66.658 | 16.118 | 6.38 | 6.38 | 3.10 |
| 18 | E | 66.658 | 16.118 | 6.24 | 6.24 | 3.10 |

The three fully symmetric A modes (7, 11, 15) carry almost all of the kernel; at the 3.10 eV peak of mode 11 the
diagonal channels dominate (|Γ^{xx}| = 36.7, |Γ^{yy}| = 34.7, |Γ^{zz}| = 35.2 Å²/eV, off-diagonal ≤ 2.1 Å²/eV), as
expected for a Raman-like driving of an A mode in S4. The E modes come in degenerate pairs whose individual values
are gauge dependent; their pair sums are small (≤ 23 Å²/eV) and do not compete with mode 11.

## 6. Compute

See `jobs.log` (one line per Slurm job). Total: 8.59 node-hours of the 20 node-hour budget
(DFPT 3×3×3 q-grid 2.39; EPW 48³ 0.41 on 1 node; EPW 72³ 1.71 on 2 nodes; EPW 96³ 3.18 on 4 nodes (47:41);
plus short scf/nscf/bands/test jobs, ~0.9 in total including the earlier sessions' failed EPW attempts).
Partitions: debug for the 13 s scf, small for everything else (on 2026-10-17 the scheduler estimated a 7 h wait on
small vs 36 h on standard for the 96³ job; it actually started after 3 h 48 min). A 1-node backup copy of the
96³ job was queued to catch backfill; it found the 4-node job running and exited after 3 s.
Wall clock: start 2026-10-16 ≈ 01:35 UTC (first session) → DONE 2026-10-17 11:15 UTC ≈ 33.7 h
(RESULT.json `wall_hours`). The sessions were interrupted twice by account usage limits; the cluster work continued.

## 7. Caveats

- The kernel variant in this build evaluates the triangle (Raman-like) diagram Γ_c only; the vertex-correction
  diagram with g^{s;α} is marked out of scope ("v1") in `indabs.f90`.
- PBE gap (2.28 eV) without GW or scissor; photon energies of the features are therefore PBE values.
- Internal coordinates taken from the sealed structure (forces already < 4e-5 Ry/bohr).
- Wannier interpolation degrades above ~12.3 eV (top of the frozen window); irrelevant for ω ≤ 6 eV.
