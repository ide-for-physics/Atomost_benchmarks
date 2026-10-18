# REPORT: light-induced coherent-phonon generation kernel, NbFeSb_mp9437

Same numbers as `RESULT.json`. Kernel file: `kernel/Gamma_alphabeta_s.dat` (identical to `kernel/Gamma_alphabeta_s_96x96x96.dat`).

## Result

| quantity | value |
|---|---|
| peak photon energy (invariant maximum, 0–6 eV) | 3.36 eV |
| peak value, I_s = Σ_{αβ} \|Γ^{αβ}_s\| (9 Cartesian channels) | 19.01 Å²/eV |
| dominant mode | Γ optical triplet at 274.8 cm⁻¹ (8.2385 THz as stored in the EPW kernel header; DFPT+ASR gives 274.86 cm⁻¹ = 8.240 THz) |
| irrep | T2 (Td site symmetry; IR- and Raman-active; strongly polar: IR intensity 30.0 (D/A)²/amu) |
| adopted mesh | 96×96×96 (fine k), coarse k-grid 8×8×8 for Wannier |
| cell | sealed structure.cif cell, not relaxed; internal positions fixed by symmetry (forces 0) |

## Method and decisions

- **DFT**: Quantum ESPRESSO 7.5 (toolchain `qe-phnlo-75`). PseudoDojo nc-fr-04 PBE standard (fully relativistic files used as scalar-relativistic, no SOC; allowed by the task). Ecut 90 Ry (PseudoDojo normal hints: Nb 82, Fe 90, Sb 80 Ry; SI uses 90 Ry). Valence Nb 13 e, Fe 16 e, Sb 15 e. Fixed occupations (insulator). SCF 8×8×8 Γ-centred, conv_thr 1e-10 Ry. Forces 0; pressure 62.5 kbar at the sealed cell (not relaxed, per task).
- **Gap**: VBM 16.9722 eV, CBM 17.5050 eV (SCF); PBE gap 0.533 eV, reproduced by the 6×6×6 and 8×8×8 NSCF grids (16.9722 / 17.5049 eV).
- **Phonons (DFPT)**: ph.x at Γ with epsil=.true., tr2_ph=1e-14 Ry (SI quotes 1e-16; 1e-14 used as the tighter practical choice). Before ASR the three triplets are 13.2 (acoustic residual), 214.9 and 274.6 cm⁻¹. `dynmat.x` with `asr='crystal'`: acoustic 0 (||Δdyn|| = 4.4e-3 Ry/bohr²), optical 214.87 cm⁻¹ (IR intensity 1.58) and 274.86 cm⁻¹ (IR intensity 30.02). Born charges Z*(Nb)=5.03, Z*(Fe)=−7.63 (ASR applied). Irrep: for a Td site symmetry each atom's displacement is T2, so both optical triplets are T2; ph.x's own labels are the same for all triplets. The 274.86 cm⁻¹ triplet is the polar one.
- **Wannier (EPW, wannier90 inside EPW)**: 22 Wannier functions: Nb s,p,d; Fe s,p,d; Sb s,p. Outer window 4.5–33 eV (DFT bands 14–35), frozen window 4.5–17 eV (bands 14–22 exactly). Bands 1–13 excluded (`bands_skipped='exclude_bands = 1:13'`; they lie >12 eV below the CBM and cannot connect to photon energies ≤ 6 eV).
- **Kernel (EPW indabs, the modified code)**: `lindabs=.true.`, degaussw (dephasing) 0.025 eV as in the SI, temps 300 K, fermi_energy 17.2377 eV (mid-gap), photon grid 0–6 eV with 0.01 eV step (601 points), coarse k 8×8×8, fine k n×n×n, q = Γ only (nq = nqf = 1).

## Wannier interpolation quality

Along the 131-point path Γ–X–W–L–Γ–K (crystal coordinates of the primitive reciprocal basis), comparing wannier90 H(R) (nbfesb_hr.dat, interpolated by numpy) with the DFT bands from the path NSCF (`logs/bands/band_compare_path.csv`, `logs/bands/band_compare_summary.txt`):

| window | RMS | max |
|---|---|---|
| valence bands 14–22, all path k | 6.2 meV | 40 meV |
| conduction states with DFT energy in [CBM, CBM+6 eV] (793 values) | 8.2 meV | 66 meV |

The conduction maximum sits at the top edge of the window (≈23.7 eV, band 28). Γ energies match DFT exactly.

Earlier attempts (kept in the job list) and why they were rejected:
- 16 WFs (Nb s,d; Fe s,d; Sb s,p), 6×6×6 grid: valence RMS 45 meV (max 226 meV), conduction RMS 312 meV (max 1.9 eV). Too few functions for the 6 eV window.
- 22 WFs, 6×6×6 grid: valence RMS 14.5 meV (max 68 meV), conduction RMS 12.4 meV (max 68 meV). The denser 8×8×8 grid brought it to the numbers above.

Caveats: the Wannier functions are poorly localised (spread ≈ 5.9–6.3 Å² each, mostly s-like). The EPW band-plot path did not write output in this build (restart-mode run), so the band comparison above uses the wannier90 Hamiltonian directly.

## Mesh convergence of the kernel

Invariant I_s(ω) = Σ over the 9 Cartesian channels of |Γ^{αβ}_s(ω)| (task definition; the papers give no explicit formula for this invariant).

| fine mesh | peak I (Å²/eV) | peak ω (eV) | mode | notes |
|---|---|---|---|---|
| 12×12×12 | 27.21 | 3.37 | 274.8 cm⁻¹ | debug partition, 32 ranks |
| 48×48×48 | 19.039 | 3.36 | 274.8 cm⁻¹ | 128 ranks, 30 min |
| 72×72×72 | 19.036 | 3.36 | 274.8 cm⁻¹ | 128 ranks, 2.0 h |
| 96×96×96 | 19.010 | 3.36 | 274.8 cm⁻¹ | 96 ranks, 6.4 h (final) |

Peak value changes by 0.15% from 48 to 96 and by 0.14% from 72 to 96. The 12-mesh value is 43% higher and is not converged.

Pointwise, the largest relative change for the dominant mode (72 vs 96, over ω with I > 0.05) is 14%, and 48 vs 96 is 44%. These differences sit in the weaker features away from the peak. The 96-mesh file is the adopted result.

Other checks:
- The three components of the 274.8 cm⁻¹ triplet (modes 7, 8, 9) give Frobenius norms √Σ|Γ|² = 10.91, 10.78, 10.66 Å²/eV at 96×96×96 (within 2.5% of each other). The per-mode sums differ (19.0, 16.9, 18.0) only because EPW's degenerate eigenvector basis is arbitrary. The Frobenius norm is the rotation-invariant cross-check (also reported for each mode in the analysis script's output).
- The response is zero below the 0.53 eV gap, as expected for an insulator; I ≈ 4.3 Å²/eV at 2 eV (12-mesh) is the onset of the interband channel.

## Known issues and caveats (from the implementation note and observed behaviour)

- **ω = 0 row is NaN for every mode.** The prefactor 1/(ħω)² diverges at ω = 0. The row is left as written by the code; the peak search excludes it.
- The note's section IV lists unresolved issues. Relevant to this run: (I) the eig_read=.FALSE. branch of vvmewan2bloch omits the `ci` factors that the eig_read=.TRUE. branch carries, which can rotate phases between A_αβ, A_α;β and K_αβ; (B) q=0 only; (C) degeneracy blocks disabled; (E) regularisation uses shifted denominators. We ran with the default eig_read=.FALSE. branch, so the (I) inconsistency applies and the absolute scale of the kernel is not validated against the reference.
- The output is the code's frequency-resolved Lorentzian (degaussw as dephasing), not a Kramers–Kronig static evaluation, per the note's section III.A.
- Direct absorption (dirabs) also runs inside the same EPW call; its output is not used.
- Occupations use a single fixed Fermi level at mid-gap (note section IV.G).

## Compute

Node-hours: Slurm AllocCPUS/256 × elapsed (AllocCPUS counts hardware threads; 256 per node). Total **9.42 node-hours** (budget 20). Breakdown and every job id are in `jobs.log`. Largest entries: 96-mesh kernel 6.42, 72-mesh kernel 2.00, 48-mesh kernel 0.50; the rest are debug-partition jobs.

Failed or cancelled jobs (all listed in `jobs.log`): 1st SCF (pseudo_dir), several EPW input and window errors, a kernel-24 test that hit the 10-min debug limit, two 96-mesh attempts that ran out of memory (1 node × 128 ranks; 2 nodes × 64 ranks at the default 112 GB per node), two 96-mesh attempts that failed at launch (interconnect configuration), and one run that was cancelled while the 72 mesh was being re-chained. The final 96 run used 1 exclusive node, 96 ranks, `--mem=240G`.

Wall clock: first file 15:34 (container clock, UTC) to DONE ≈ 03:44 next day, 12.2 h.

## Files

- Inputs: `inputs/` (scf.in, ph.in, nscf_k6.in, nscf_k8.in, bands_path.in, epw_wan.in, epw_wan8.in, epw_band.in, epw_kern{12,24,48,72,96}.in, job_*.sh, dynmat.in, path.dat, analyze_kernel.py, check_bands.py). The wannier90 input and output: `logs/wannier/`.
- Outputs: `logs/dft/` (SCF, DFPT, NSCF, dynmat output), `logs/epw/` (EPW logs), `logs/bands/` (band comparison data), `logs/kernel/` (raw kernel files and analysis).
- Kernel: `kernel/Gamma_alphabeta_s.dat` (= 96³), `kernel/Gamma_alphabeta_s_{12,48,72,96}x*.dat`.
- `jobs.log`, `NOTES.md`, `RESULT.json`, `DONE`.

## Shared-account note

The LUMI login account is `<user>`. `squeue` shows other NbFeSb and benchmark jobs under this account that were not submitted by this run. They were not cancelled, modified or used; only the `small` and `debug` partitions were used for the runs listed here, with no reservations.
