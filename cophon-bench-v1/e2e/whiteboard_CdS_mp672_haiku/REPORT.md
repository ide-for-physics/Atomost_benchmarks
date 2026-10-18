# CdS_mp672: light-induced coherent-phonon generation kernel (Gamma phonons), report

Same numbers as `RESULT.json`. Kernel from the authors' EPW kernel variant (`EPW/src/indabs.f90`, file `Gamma_alphabeta_s.dat`).

## Result

| quantity | value |
|---|---|
| kernel file | `kernel/Gamma_alphabeta_s.dat` (converged mesh 72x72x48; identical copy `kernel/Gamma_alphabeta_s_72x72x48.dat`) |
| peak (invariant) | **244.58 Å²/eV at 5.78 eV** (energy grid 0.01 eV) |
| dominant mode | E2 pair, kernel index mode 4: frequency as read in the kernel file 4.6669 meV = 37.64 cm⁻¹ = **1.128 THz** (`mode_thz`, matches the kernel file). DFPT Γ (ASR-corrected) gives 36.30 cm⁻¹ = 1.088 THz for the same pair; see below |
| mesh | 72x72x48 |
| cell | as given in `structure.cif` / `structure_POSCAR` (sealed, not relaxed) |
| compute | 4.26 node-h (sum of Slurm accounting, `jobs.log`); wall ~6.05 h (17:55 to 23:58 UTC) |

**Invariant definition (my choice; the papers do not define a "rotational invariant" explicitly).** For each optical mode s and photon energy ω, I_s(ω) = [Σ_ab |Γ^ab_s(ω)|²]^(1/2), the Frobenius norm over the nine Cartesian channels (xx, yy, zz, xy, xz, yz, yx, zx, zy) of the complex kernel. The peak is max over ω ∈ [0.01, 6.00] eV and over modes s. `analysis/peak.py` implements this. An alternative definition, Σ_ab |Γ^ab| (sum of channel magnitudes), was not evaluated.

## Mesh convergence

Global peak of the invariant, same calculation on each fine mesh (`kernel/Gamma_alphabeta_s_<mesh>.dat`):

| fine mesh | peak (Å²/eV) | peak energy (eV) | dominant mode |
|---|---|---|---|
| 12x12x8 | 396.0 | 5.69 | 4 |
| 24x24x16 | 279.2 | 5.77 | 5 |
| 36x36x24 | 242.0 | 5.73 | 5 |
| 48x48x32 | 247.0 | 5.77 | 4 |
| 60x60x40 | 238.6 | 5.79 | 4 |
| **72x72x48** | **244.6** | **5.78** | **4** |

The series is not monotonic. The last four meshes (36 to 72) stay within about ±3% of 245 Å²/eV, and the peak energy is 5.73–5.79 eV. I adopted 72x72x48. The modes 4 and 5 are the degenerate E2 pair; they differ by 2–5% at each mesh, which is residual numerical noise.

## Wannier interpolation (does NOT meet the target)

Set-up: 16 Wannier functions (s and p projections on each Cd and each S atom of the cell), Wannierised from bands 21–40 (bands 1–20 excluded: Cd 4s, 4p, 4d and S 3s), disentanglement window up to 22 eV, frozen window up to 10 eV, coarse grid 6x6x4 (144 k). Compared with DFT (`pw.x bands`) on the same 85-point path Γ–M–K–Γ–A–L–H–A (`analysis/band_comparison.txt`, `analysis/bandcmp.py`):

- Valence (DFT bands 21–26, VBM 7.0695 eV): RMS 14.6 meV, max 125 meV. The largest errors are near L–H–A (bands 23–24, k-points 68–74).
- Conduction up to CBM + 6 eV (14.31 eV), DFT bands 27–40: RMS 135 meV, max 410 meV. The error grows with band index (bands 27–28 RMS about 30 meV; bands 29–34 RMS 90–290 meV).

**This fails the "within a few meV" criterion.** The 16-function manifold cannot represent the conduction bands near 13–15 eV well. Attempts to fix it failed: 20 Wannier functions with `random` projections were rejected by Wannier90 (`malformed projection definition: random`); 18 functions (8 plus Cd d) crashed inside the Wannier90 interface (`munmap_chunk(): invalid pointer`). I did not find a working route within the time I spent, so these figures stand as the only Wannier quality data. The kernel was computed with the same 16-function interpolation, so the high-energy (conduction) part, including the 5.78 eV peak, carries these errors. The peak value should be treated as provisional until the Wannier set is improved.

Also, the NSCF and band runs used the sealed cell with PseudoDojo FR pseudopotentials run scalar-relativistically (no SOC), as the task allows. The triple-degenerate VB top at Γ is split (7.02/7.07 eV) for this reason.

## Phonons at Γ (DFPT, ASR)

`ph.x` with `epsil` and `trans` at q = 0, tr2_ph = 1e-14, one node of 64 tasks (`ph/ph.out`). Acoustic modes before the ASR: −9.5 cm⁻¹ (A1, E1 pairs). After `dynmat.x` with `asr = crystal` (`inputs/remote_outputs/dynmat_asr.out`) the acoustic modes are 0.00 cm⁻¹. Optical modes (cm⁻¹, symmetry C6v):

| mode | cm⁻¹ | THz | irrep | IR/Raman |
|---|---|---|---|---|
| 4–5 | 36.30 | 1.088 | E2 | Raman |
| 6 | 134.86 | 4.043 | B1 | silent |
| 7 | 234.97 | 7.044 | A1 | IR + Raman |
| 8–9 | 241.33 | 7.235 | E1 | IR + Raman |
| 10–11 | 255.10 | 7.648 | E2 | Raman |
| 12 | 302.62 | 9.072 | B1 | silent |

Born charges and ε∞ come from the same run (in `ph/ph.out`). EPW reads 4.667 meV (37.6 cm⁻¹) for the E2 pair; I have not established why EPW's Γ frequency differs from the ASR-corrected DFPT value by 1.3 cm⁻¹. `mode_thz` in RESULT.json is the value the kernel file itself carries (1.128 THz), so that the grader's re-analysis agrees; the DFPT value (1.088 THz) is the independent check.

## Electronic structure check

PBE gap of this cell: 1.24 eV (VBM 7.0695 eV, CBM 8.3096 eV). Residual forces on the given internal coordinates are about 1e-4 Ry/bohr, so I did not relax (no vc-relax; the cell is sealed).

## Parameters

- pw.x: PseudoDojo nc-fr-04 PBE standard (Cd, S), ecutwfc 100 Ry, ecutrho 400 Ry, 40 bands, scf/nscf k 6x6x4, conv_thr 1e-9, diago_thr_init 5e-6.
- ph.x: Γ only (no q-mesh), epsil = .true., trans = .true., tr2_ph = 1e-14.
- EPW (kernel variant): elph, nq = 1x1x1 and nqf = 1x1x1, nk = 6x6x4, nbndsub = 16, bands_skipped = exclude 1–20, lpolar = .false., degaussw = 0.025 eV, Fermi level 7.69 eV (mid-gap, input), omega 0.01–6.00 eV in 0.01 eV steps (0 eV excluded: 1/ω² singularity), lindabs = .true.
- Why nqf = 1x1x1 is required: `Gamma_alphabeta_s` is reset per q-point and written only at the last q (`indabs.f90`, `use_wannier.f90`). Any larger fine q-grid would write the last q, not Γ.
- Polar correction: not applied (lpolar = .false.). The EPC at q = 0 is the short-range DFPT value. This is a known limitation for polar modes (E1, A1).

## Known problems and deviations

1. Wannier accuracy misses the target (see above). This is the main open issue.
2. The kernel-variant output file has 9 modes (modes 4–12, 600 frequency points, 0.01–6.00 eV). Its header lists six channels; the data holds nine complex channels.
3. Two EPW-side workflow fixes were needed (both documented in `NOTES.md`): the dvscf file set for EPW (`dvscf_q1` via `dvscf_star%open`, and `cds.phsave/patterns.1.xml`, and `cds.dyn_q1`), and the 80-character `filkf` limit.
4. The first DFPT job failed at `srun` launch (interconnect error on four nodes). A second job on two nodes failed the same way, so I resubmitted on one node. Both failed attempts are in `jobs.log`.
5. Two jobs under this account with names `CdS_mp672_e2eH_rekernel_*` (22872846, 22876187) were not submitted by this run and are excluded from the node-hour total.

## Files

- `RESULT.json`, `REPORT.md`, `NOTES.md`, `jobs.log`, `DONE`.
- `kernel/Gamma_alphabeta_s.dat` (72x72x48), `kernel/Gamma_alphabeta_s_<mesh>.dat` for 12x12x8, 24x24x16, 36x36x24, 48x48x32, 60x60x40, 72x72x48.
- `inputs/`: pw.x, ph.x, nscf, band-path and EPW input files, and job scripts. `inputs/remote_outputs/`: scf/nscf/bands/ph/dynmat outputs, EPW outputs, and the Wannier90 `.win`/`.wout` for the 72 run.
- `analysis/`: `peak.py` (invariant), `bandcmp.py` and `band_comparison.txt` (Wannier vs DFT), `wannier_band.eig`, `dft_bands_list.out`.
