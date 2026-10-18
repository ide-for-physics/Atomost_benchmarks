# GaP_t1_e2eH coherent-phonon report — Gamma-only DFPT, scalar Wannier state, 0.03–6 eV Γc kernel

Generated 2026-10-15T13:23:17+02:00 by `workflow/lib/report.py` from the files under `<cophon>/benchmarks/cophon-bench-v1/e2e_library/GaP_t1_e2eH`. Every number below is read from a result or gate file; nothing is typed in by hand.

**Outcome: GaP_t1_e2eH has a Γc coherent-phonon kernel on the 96×96×96 fine k-mesh.** 3 optical Γ-point modes (44.53, 44.53, 44.53 meV) over 0.03–6.00 eV at 300 K with 0.03 eV smearing. The basis-independent invariant peaks at 2.82 eV (16.05 Å²/eV); under the 0.35 V/Å, 8 fs pulse convention the invariant amplitude peak is 1.642 Å at 2.82 eV (largest single mode 0.652 Å). First non-zero response at 1.77 eV. Between the last two meshes (k80 → k96) the 0.10 eV envelope changes by 1.05 % (limit 3 %; raw spectrum 9.0 %), so the kernel is converged on the envelope.

Scope: Γc only (no Γe vertex correction), scalar-relativistic, PBE gap, Gamma-only DFPT (one q-point, `ldisp = .true.`, `nq = 1 1 1`); velocities from EPW's `vme = 'dipole'` route (the full velocity i[H,r], non-local pseudopotential commutator included, computed on the coarse mesh and Wannier-interpolated; origin-free).

## Standard all-mode result (96×96×96)

![GaP_t1_e2eH all optical modes and all tensor directions, unified scale](figures/gap_t1_e2eh_all_modes_k96_sharey.png)

![GaP_t1_e2eH all optical modes, per-panel scale](figures/gap_t1_e2eh_all_modes_k96.png)

![GaP_t1_e2eH mode-channel peak heatmap](figures/gap_t1_e2eh_mode_channel_heatmap_k96.png)

![GaP_t1_e2eH optical-mode invariant and channel resolution](figures/gap_t1_e2eh_invariant_k96.png)

| Quantity (96×96×96, 0.03 eV smearing, 300 K) | Value |
|---|---|
| Invariant \|Γ\| peak | 16.05 Å²/eV at 2.82 eV |
| Envelope (0.10 eV) peak | 11.98 Å²/eV at 2.91 eV |
| Invariant amplitude peak (0.35 V/Å, 8 fs) | 1.642 Å at 2.82 eV |
| Per-mode amplitude peaks (basis-dependent split) | 0.542 / 0.652 / 0.547 Å |
| Mode-summed channel peaks, diagonal (xx, yy, zz) | 0.05–0.05 Å²/eV |
| Mode-summed channel peaks, off-diagonal (xy, xz, yz, yx, zx, zy) | 6.55–6.55 Å²/eV |
| Diagonal / off-diagonal peak ratio | 0.008 |
| First non-zero response | 1.77 eV |
| Photon grid | 0.03–6.00 eV, 200 points |

## Electronic structure and Wannier state

| Quantity | Value |
|---|---|
| PBE band edges (VBM / CBM) | 7.637 / 9.228 eV (gap 1.591 eV) |
| Consumer shell (must be interpolated well) | 2.93 … 13.94 eV |
| Frozen / outer window | 0.83 … 15.94 eV / 0.83 … 31.93 eV |
| Wannier functions | 12 (Ga:s;p, P:p;d); recipe source: v1.1 |
| Accepted Wannier round | round 1 (1 round gate on file, including any before an electron recompute); max spread 2.90 Å², band RMS 2.2 meV, worst 19.2 meV in the shell (limits 10 Å², 50 / 25 meV) |
| EPW-side interpolation (same shell, from the EPW1 Wannier files) | RMS 2.2 meV, worst 19.2 meV → PASS |

![GaP_t1_e2eH DFT bands versus the Wannier interpolation, with the shell and windows](figures/gap_t1_e2eh_bands_dft_vs_wannier.png)

## Γ-point phonons (DFPT)

| Mode | ω (cm⁻¹) | ω (meV) |
|---|---:|---:|
| optical 4 | 359.18 | 44.53 |
| optical 5 | 359.18 | 44.53 |
| optical 6 | 359.18 | 44.53 |

Acoustic sum rule applied (dynmat.x); acoustic modes after ASR -0.00, -0.00, 0.00 cm⁻¹ (raw -2.84, -2.84, -2.84 cm⁻¹). ε∞ diagonal 10.70, 10.70, 10.70; largest |Z*| 2.17; polar: True. Gate: PASS. Softness: stiff (tier 0).

## Velocity-route check

Wannier centres sit up to 2.36 Å from the cell origin (b·r max 0.47); EPW's `wannier` velocity route would carry an origin-dependent error of about 4 % at worst (1.2 % on average) for this cell.

| Adopted mesh | Production route | Other route | Envelope difference | Tensor difference | Invariant peak (production / other) | Forbidden-channel ratio (production / other) | Verdict |
|---|---|---|---:|---:|---|---|---|
| k96 | dipole | wannier | 0.4 % (limit 5 %) | 2.2 % | 16.05 / 16.10 Å²/eV | 0.008 / 0.024 | PASS |

Reading: the two velocity routes agree.

## Fine-k convergence

Convergence is judged on the 0.10 eV Gaussian envelope of the invariant (gate: consecutive rel-L2 <= 0.03); the raw rel-L2 is reported, not gated.

| Meshes | raw rel-L2 | raw Pearson | envelope rel-L2 | envelope peak | gate |
|---|---:|---:|---:|---|---|
| 48×48×48 → 64×64×64 | 0.200 | 0.967 | 0.051 | 12.15 → 11.98 Å²/eV, 2.91 → 2.94 eV | FAIL |
| 64×64×64 → 80×80×80 | 0.138 | 0.984 | 0.033 | 11.98 → 11.96 Å²/eV, 2.94 → 2.91 eV | FAIL |
| 80×80×80 → 96×96×96 | 0.090 | 0.993 | 0.010 | 11.96 → 11.98 Å²/eV, 2.91 → 2.91 eV | PASS |

![GaP_t1_e2eH fine-k convergence](figures/kmesh_convergence.png)

Per-mesh overlay of the raw invariant, its envelope, and the change between consecutive meshes (the top 0.2 eV of the window is excluded from the gate):

![GaP_t1_e2eH per-mesh overlay](figures/kmesh_overlay.png)

## What was done

1. **intake**: ACCEPTED — GaP sg 216 nbnd 29
2. **relax**: ACCEPTED, job 22861439 (debug, COMPLETED) — max force 0.0 Ry/bohr, pressure -0.25 kbar
3. **electron**: ACCEPTED, job 22861714 (debug, COMPLETED) — gap 1.591 eV; PDOS 5 shells; trim: 6 bands excluded (gap 2.696 eV); v1.1 recipe from the superset stage
4. **wannier**: ACCEPTED, job 22862591 (small, COMPLETED) — round 1: score 0.099 <= 0.9 (W7); wout_present=ok; final_state=ok; num_wann_in_wout=ok; spread_max=ok; plateau_drift=ok; localisation_converged=ok; ran_out_of_steps=ok; all_done=ok; disentanglement_settled=ok; comparison_present=ok; comparator_build=ok; dense_reference_certified=ok; band_rms_meV=ok; band_worst_meV=ok; grids_equal=ok
5. **phonon**: ACCEPTED, job 22862021 (debug, COMPLETED) — max 359.18 cm-1; polar=True; softness stiff -> tier 0
6. **epw1**: ACCEPTED, job 22863382 (small, COMPLETED) — restart written; EPW bands within the shell bars
7. **kernel**: ACCEPTED, job 22871039 (debug, COMPLETED) — converged at k96: envelope change 0.0105 <= 0.03 with previous 0.0335 <= 0.1; velocity-route check PASS (envelope 0.4 %, tensor 2.2 %)
8. **report**: PENDING
9. **anharmonic**: SKIPPED — tier 0: softness stiff
10. **rekernel**: SKIPPED — tier 0: softness stiff
11. **superset**: ACCEPTED, job 22861869 (small, COMPLETED) — superset 18 functions; round-1 recipe v1.1 default: 12 functions (reduced), Pmin 8

Wannier recipe (round 1, source v1.1: ["Pmin (kept bands at or below target top + 2 eV = 15.94 eV, worst k) = 8; PDOS picks ['Ga:p', 'Ga:s', 'P:p'] = 7", 'added P:d: P = 12']): 12 functions, projections ['Ga:s;p', 'P:p;d'], exclude_bands [1, 2, 3, 4, 5, 6], outer window [0.8297, 31.9267] eV, frozen window [0.8297, 15.937] eV, consumer shell [2.928, 13.937] eV.

Electronic policy: ecutwfc 80 Ry, ecutrho 320 Ry, SCF mesh [10, 10, 10], NSCF mesh [10, 10, 10], nbnd 29, relax `fixed`, spacegroup F-43m (216), nat 2.

## Validation gates

| Gate file | Status | Key numbers | Reasons |
|---|---|---|---|
| `gate_electron` | PASS | — | — |
| `gate_epw1` | PASS | — | — |
| `gate_kernel_k48` | PASS | — | — |
| `gate_kernel_k64` | PASS | — | — |
| `gate_kernel_k80` | PASS | — | — |
| `gate_kernel_k96` | PASS | — | — |
| `gate_kernel_k96_eta030` | PASS | — | — |
| `gate_phonon` | PASS | optical_max_cm1 359.2; acoustic_cm1_asr [-0.0, -0.0, 0.0]; max_abs_zstar 2.172; polar True | — |
| `gate_relax` | PASS | — | — |
| `gate_route_check` | PASS | — | — |
| `gate_superset` | PASS | — | — |
| `gate_wannier_round1` | PASS | — | — |

Standing limits: Wannier spreads <= 10 Å², band RMS <= 50 meV and worst <= 25 meV in the consumer shell, Γ acoustic modes within 1 cm⁻¹ after ASR, envelope rel-L2 <= 0.03.

## Scope, limits, and next safe action

- **Γc only.** The triangle term Γc is computed; the vertex correction Γe is absent.
- **Scalar-relativistic, PBE gap.** No spin-orbit coupling and no gap correction; the onset follows the PBE gap, so absolute peak positions cannot be compared with experiment without a scissor.
- **Gamma-only DFPT.** Phonons are computed at q = 0 only; the LO–TO splitting is not resolved at exactly Γ and no off-Γ stability check exists in this route.
- **Forbidden-channel residual.** Diagonal / off-diagonal mode-summed peak ratio 0.008; which channels are symmetry-forbidden depends on the point group and must be judged for this material.
- **Convergence.** Envelope rel-L2 0.0105 and raw rel-L2 0.090 between 80×80×80 and 96×96×96.

## Run record

- Workflow baseline at creation: v2.0.12 (sealed 2026-10-15, manifest `e8050e6a9f5b…`, tree clean)
- Cell policy: pbesol (cell relaxed with PBEsol, internal coordinates and every later stage with PBE); production cell: input
- Phonon tier: 0 (softness stiff, lowest optical mode 359.18 cm⁻¹, threshold 60.0 cm⁻¹)
- Material workflow dir: `<cophon>/benchmarks/cophon-bench-v1/e2e_library/GaP_t1_e2eH`
- LUMI run root: `/scratch/project_<id>/<user>/theory2code/cphon/runs/GaP_t1_e2eH/wf`
- Job ledger: `JOB_LEDGER.md` (one row per submitted job)
- Jobs: electron 22861714 (debug, COMPLETED); epw1 22863382 (small, COMPLETED); kernel 22871039 (debug, COMPLETED); phonon 22862021 (debug, COMPLETED); relax 22861439 (debug, COMPLETED); superset 22861869 (small, COMPLETED); wannier 22862591 (small, COMPLETED)
- Kernel files (SHA-256): k48 `45715b707270…`; k64 `91993f43943b…`; k80 `357bdd0f5907…`; k96 `fc8f5f54f328…`
- 2026-10-15T12:58:20+02:00: ROUTE — kernel: debug — estimated start in 0.4 h (after a slot frees: debug: 2 of the user's 2 submitted jobs); debug 0.4 h (debug: 2 of the user's 2 submitted jobs); small 0.57 h; standard 17.22 h
- 2026-10-15T12:59:57+02:00: ROUTE — kernel: debug — estimated start in 0.4 h (after a slot frees: debug: 2 of the user's 2 submitted jobs); debug 0.37 h (debug: 2 of the user's 2 submitted jobs); small 0.63 h; standard 17.18 h
- 2026-10-15T13:01:35+02:00: ROUTE — kernel: debug — estimated start in 0.1 h; debug 0.12 h; small 0.61 h; standard 17.25 h
- 2026-10-15T13:01:39+02:00: kernel:SUBMIT — job 22870275 on debug in /scratch/project_<id>/<user>/theory2code/cphon/runs/GaP_t1_e2eH/wf/kernel
- 2026-10-15T13:12:23+02:00: kernel:COLLECTED — k96: 51 files pulled
- 2026-10-15T13:12:23+02:00: kernel:PENDING — converged at k96: envelope change 0.0105 <= 0.03 with previous 0.0335 <= 0.1; velocity-route check queued at k96
- 2026-10-15T13:12:26+02:00: ROUTE — kernel: debug — estimated start in 0.1 h; debug 0.07 h; small 0.88 h; standard 17.07 h
- 2026-10-15T13:12:30+02:00: kernel:SUBMIT — job 22871039 on debug in /scratch/project_<id>/<user>/theory2code/cphon/runs/GaP_t1_e2eH/wf/kernel
- 2026-10-15T13:23:16+02:00: kernel:COLLECTED — k96_eta030: 61 files pulled
- 2026-10-15T13:23:16+02:00: kernel:ACCEPTED — converged at k96: envelope change 0.0105 <= 0.03 with previous 0.0335 <= 0.1; velocity-route check PASS (envelope 0.4 %, tensor 2.2 %)
