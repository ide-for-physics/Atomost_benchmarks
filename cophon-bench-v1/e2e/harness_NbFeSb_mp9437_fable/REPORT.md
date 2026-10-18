# NbFeSb_mp9437_e2eF coherent-phonon report — Gamma-only DFPT, scalar Wannier state, 0.03–6 eV Γc kernel

Generated 2026-10-15T18:39:22+02:00 by `workflow/lib/report.py` from the files under `<cophon>/benchmarks/cophon-bench-v1/e2e_library/NbFeSb_mp9437_e2eF`. Every number below is read from a result or gate file; nothing is typed in by hand.

**Outcome: NbFeSb_mp9437_e2eF has a Γc coherent-phonon kernel on the 64×64×64 fine k-mesh.** 6 optical Γ-point modes (26.62, 26.62, 26.62, 34.14, 34.14, 34.14 meV) over 0.03–6.00 eV at 300 K with 0.03 eV smearing. The basis-independent invariant peaks at 3.36 eV (21.50 Å²/eV); under the 0.35 V/Å, 8 fs pulse convention the invariant amplitude peak is 2.608 Å at 3.36 eV (largest single mode 0.822 Å). First non-zero response at 1.17 eV. Between the last two meshes (k48 → k64) the 0.10 eV envelope changes by 0.19 % (limit 3 %; raw spectrum 1.6 %), so the kernel is converged on the envelope.

Scope: Γc only (no Γe vertex correction), scalar-relativistic, PBE gap, Gamma-only DFPT (one q-point, `ldisp = .true.`, `nq = 1 1 1`); velocities from EPW's `vme = 'dipole'` route (the full velocity i[H,r], non-local pseudopotential commutator included, computed on the coarse mesh and Wannier-interpolated; origin-free).

## Standard all-mode result (64×64×64)

![NbFeSb_mp9437_e2eF all optical modes and all tensor directions, unified scale](figures/nbfesb_mp9437_e2ef_all_modes_k64_sharey.png)

![NbFeSb_mp9437_e2eF all optical modes, per-panel scale](figures/nbfesb_mp9437_e2ef_all_modes_k64.png)

![NbFeSb_mp9437_e2eF mode-channel peak heatmap](figures/nbfesb_mp9437_e2ef_mode_channel_heatmap_k64.png)

![NbFeSb_mp9437_e2eF optical-mode invariant and channel resolution](figures/nbfesb_mp9437_e2ef_invariant_k64.png)

| Quantity (64×64×64, 0.03 eV smearing, 300 K) | Value |
|---|---|
| Invariant \|Γ\| peak | 21.50 Å²/eV at 3.36 eV |
| Envelope (0.10 eV) peak | 13.92 Å²/eV at 3.39 eV |
| Invariant amplitude peak (0.35 V/Å, 8 fs) | 2.608 Å at 3.36 eV |
| Per-mode amplitude peaks (basis-dependent split) | 0.532 / 0.567 / 0.579 / 0.770 / 0.816 / 0.822 Å |
| Mode-summed channel peaks, diagonal (xx, yy, zz) | 0.04–0.06 Å²/eV |
| Mode-summed channel peaks, off-diagonal (xy, xz, yz, yx, zx, zy) | 8.77–8.78 Å²/eV |
| Diagonal / off-diagonal peak ratio | 0.007 |
| First non-zero response | 1.17 eV |
| Photon grid | 0.03–6.00 eV, 200 points |

## Electronic structure and Wannier state

| Quantity | Value |
|---|---|
| PBE band edges (VBM / CBM) | 16.972 / 17.505 eV (gap 0.533 eV) |
| Consumer shell (must be interpolated well) | 11.21 … 23.27 eV |
| Frozen / outer window | 10.91 … 25.27 eV / 10.91 … 39.41 eV |
| Wannier functions | 24 (Nb:s;d, Fe:s;p;d, Sb:s;p;d); recipe source: ladder |
| Accepted Wannier round | round 2 (2 round gates on file, including any before an electron recompute); max spread 3.44 Å², band RMS 0.7 meV, worst 7.4 meV in the shell (limits 10 Å², 50 / 25 meV) |
| EPW-side interpolation (same shell, from the EPW1 Wannier files) | RMS 0.7 meV, worst 7.4 meV → PASS |

![NbFeSb_mp9437_e2eF DFT bands versus the Wannier interpolation, with the shell and windows](figures/nbfesb_mp9437_e2ef_bands_dft_vs_wannier.png)

## Γ-point phonons (DFPT)

| Mode | ω (cm⁻¹) | ω (meV) |
|---|---:|---:|
| optical 4 | 214.65 | 26.61 |
| optical 5 | 214.65 | 26.61 |
| optical 6 | 214.65 | 26.61 |
| optical 7 | 275.44 | 34.15 |
| optical 8 | 275.44 | 34.15 |
| optical 9 | 275.44 | 34.15 |

Acoustic sum rule applied (dynmat.x); acoustic modes after ASR -0.00, -0.00, 0.00 cm⁻¹ (raw 2.55, 2.55, 2.55 cm⁻¹). ε∞ diagonal 24.02, 24.02, 24.02; largest |Z*| 7.63; polar: True. Gate: PASS. Softness: stiff (tier 0).

## Velocity-route check

Wannier centres sit up to 6.00 Å from the cell origin (b·r max 1.11); EPW's `wannier` velocity route would carry an origin-dependent error of about 20 % at worst (7.2 % on average) for this cell — above the warning level.

| Adopted mesh | Production route | Other route | Envelope difference | Tensor difference | Invariant peak (production / other) | Forbidden-channel ratio (production / other) | Verdict |
|---|---|---|---:|---:|---|---|---|
| k64 | dipole | wannier | 1.8 % (limit 5 %) | 6.5 % | 21.50 / 21.47 Å²/eV | 0.007 / 0.037 | PASS |

Reading: the two velocity routes agree.

## Fine-k convergence

Convergence is judged on the 0.10 eV Gaussian envelope of the invariant (gate: consecutive rel-L2 <= 0.03); the raw rel-L2 is reported, not gated.

| Meshes | raw rel-L2 | raw Pearson | envelope rel-L2 | envelope peak | gate |
|---|---:|---:|---:|---|---|
| 48×48×48 → 64×64×64 | 0.016 | 1.000 | 0.002 | 13.92 → 13.92 Å²/eV, 3.39 → 3.39 eV | PASS |

![NbFeSb_mp9437_e2eF fine-k convergence](figures/kmesh_convergence.png)

Per-mesh overlay of the raw invariant, its envelope, and the change between consecutive meshes (the top 0.2 eV of the window is excluded from the gate):

![NbFeSb_mp9437_e2eF per-mesh overlay](figures/kmesh_overlay.png)

## What was done

1. **intake**: ACCEPTED — NbFeSb sg 216 nbnd 55
2. **relax**: ACCEPTED, job 22862620 (debug, COMPLETED) — max force 0.0 Ry/bohr, pressure 0.07 kbar
3. **electron**: ACCEPTED, job 22862778 (debug, COMPLETED) — gap 0.533 eV; PDOS 9 shells; trim: 14 bands excluded (gap 3.693 eV); v1.1 recipe from the superset stage
4. **wannier**: ACCEPTED, job 22865516 (small, COMPLETED) — round 2: score 0.079 <= 0.9 (W7); wout_present=ok; final_state=ok; num_wann_in_wout=ok; spread_max=ok; plateau_drift=ok; localisation_converged=ok; ran_out_of_steps=ok; all_done=ok; disentanglement_settled=ok; comparison_present=ok; comparator_build=ok; dense_reference_certified=ok; band_rms_meV=ok; band_worst_meV=ok; grids_equal=ok
5. **phonon**: ACCEPTED, job 22863132 (debug, COMPLETED) — max 275.44 cm-1; polar=True; softness stiff -> tier 0
6. **epw1**: ACCEPTED, job 22871982 (small, COMPLETED) — restart written; EPW bands within the shell bars
7. **kernel**: ACCEPTED, job 22877431 (small, COMPLETED) — converged at k64: first pair 0.0019 <= 0.003 (a tenth of the limit): converged without a second step; velocity-route check PASS (envelope 1.8 %, tensor 6.5 %)
8. **report**: PENDING
9. **anharmonic**: SKIPPED — tier 0: softness stiff
10. **rekernel**: SKIPPED — tier 0: softness stiff
11. **superset**: ACCEPTED, job 22863000 (small, COMPLETED) — superset 27 functions; round-1 recipe casebook (NbFeSb_mp9437_kp): 24 functions (reduced), Pmin 18

Wannier recipe (round 2, source ladder: ['num_iter 1000 -> 4000: only the disentangled subspace did not settle (v1.1: more iterations, same recipe)']): 24 functions, projections ['Nb:s;d', 'Fe:s;p;d', 'Sb:s;p;d'], exclude_bands [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], outer window [10.9058, 39.4097] eV, frozen window [10.9058, 25.272] eV, consumer shell [11.205, 23.272] eV.

Electronic policy: ecutwfc 90 Ry, ecutrho 360 Ry, SCF mesh [10, 10, 10], NSCF mesh [10, 10, 10], nbnd 55, relax `fixed`, spacegroup F-43m (216), nat 3.

## Validation gates

| Gate file | Status | Key numbers | Reasons |
|---|---|---|---|
| `gate_electron` | PASS | — | — |
| `gate_epw1` | PASS | — | — |
| `gate_kernel_k48` | PASS | — | — |
| `gate_kernel_k64` | PASS | — | — |
| `gate_kernel_k64_eta030` | PASS | — | — |
| `gate_phonon` | PASS | optical_max_cm1 275.4; acoustic_cm1_asr [-0.0, -0.0, 0.0]; max_abs_zstar 7.626; polar True | — |
| `gate_relax` | PASS | — | — |
| `gate_route_check` | PASS | — | — |
| `gate_superset` | PASS | — | — |
| `gate_wannier_round1` | FAIL | — | DISENTANGLEMENT_NOT_SETTLED |
| `gate_wannier_round2` | PASS | — | — |

Standing limits: Wannier spreads <= 10 Å², band RMS <= 50 meV and worst <= 25 meV in the consumer shell, Γ acoustic modes within 1 cm⁻¹ after ASR, envelope rel-L2 <= 0.03.

## Scope, limits, and next safe action

- **Γc only.** The triangle term Γc is computed; the vertex correction Γe is absent.
- **Scalar-relativistic, PBE gap.** No spin-orbit coupling and no gap correction; the onset follows the PBE gap, so absolute peak positions cannot be compared with experiment without a scissor.
- **Gamma-only DFPT.** Phonons are computed at q = 0 only; the LO–TO splitting is not resolved at exactly Γ and no off-Γ stability check exists in this route.
- **Forbidden-channel residual.** Diagonal / off-diagonal mode-summed peak ratio 0.007; which channels are symmetry-forbidden depends on the point group and must be judged for this material.
- **Convergence.** Envelope rel-L2 0.0019 and raw rel-L2 0.016 between 48×48×48 and 64×64×64.

## Run record

- Workflow baseline at creation: v2.0.12 (sealed 2026-10-15, manifest `e8050e6a9f5b…`, tree clean)
- Cell policy: pbesol (cell relaxed with PBEsol, internal coordinates and every later stage with PBE); production cell: input
- Phonon tier: 0 (softness stiff, lowest optical mode 214.65 cm⁻¹, threshold 60.0 cm⁻¹)
- Material workflow dir: `<cophon>/benchmarks/cophon-bench-v1/e2e_library/NbFeSb_mp9437_e2eF`
- LUMI run root: `/scratch/project_<id>/<user>/theory2code/cphon/runs/NbFeSb_mp9437_e2eF/wf`
- Job ledger: `JOB_LEDGER.md` (one row per submitted job)
- Jobs: electron 22862778 (debug, COMPLETED); epw1 22871982 (small, COMPLETED); kernel 22877431 (small, COMPLETED); phonon 22863132 (debug, COMPLETED); relax 22862620 (debug, COMPLETED); superset 22863000 (small, COMPLETED); wannier 22865516 (small, COMPLETED)
- Kernel files (SHA-256): k48 `7246a524c835…`; k64 `1666483c8fc5…`
- 2026-10-15T16:34:17+02:00: kernel:COLLECTED — k48: 21 files pulled
- 2026-10-15T16:34:17+02:00: kernel:PENDING — k48 accepted; ladder continues with k64
- 2026-10-15T16:34:19+02:00: ROUTE — kernel: small — estimated start in 1.2 h; standard 21.02 h; small 1.2 h
- 2026-10-15T16:34:25+02:00: kernel:SUBMIT — job 22876441 on small in /scratch/project_<id>/<user>/theory2code/cphon/runs/NbFeSb_mp9437_e2eF/wf/kernel
- 2026-10-15T17:23:09+02:00: kernel:COLLECTED — k64: 31 files pulled
- 2026-10-15T17:23:09+02:00: kernel:PENDING — converged at k64: first pair 0.0019 <= 0.003 (a tenth of the limit): converged without a second step; velocity-route check queued at k64
- 2026-10-15T17:23:11+02:00: ROUTE — kernel: small — estimated start in 2.1 h; standard 21.28 h; small 2.1 h
- 2026-10-15T17:23:16+02:00: kernel:SUBMIT — job 22877431 on small in /scratch/project_<id>/<user>/theory2code/cphon/runs/NbFeSb_mp9437_e2eF/wf/kernel
- 2026-10-15T18:39:20+02:00: kernel:COLLECTED — k64_eta030: 41 files pulled
- 2026-10-15T18:39:20+02:00: kernel:ACCEPTED — converged at k64: first pair 0.0019 <= 0.003 (a tenth of the limit): converged without a second step; velocity-route check PASS (envelope 1.8 %, tensor 6.5 %)
