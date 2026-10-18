# CdS_mp672_e2eH coherent-phonon report — Gamma-only DFPT, scalar Wannier state, 0.03–6 eV Γc kernel

Generated 2026-10-15T17:00:57+02:00 by `workflow/lib/report.py` from the files under `<cophon>/benchmarks/cophon-bench-v1/e2e_library/CdS_mp672_e2eH`. Every number below is read from a result or gate file; nothing is typed in by hand.

**Outcome: CdS_mp672_e2eH has a Γc coherent-phonon kernel on the 64×64×64 fine k-mesh.** 9 optical Γ-point modes (4.74, 4.74, 16.71, 29.06, 29.97, 29.97, 31.68, 31.68, 37.48 meV) over 0.03–6.00 eV at 300 K with 0.03 eV smearing. The basis-independent invariant peaks at 5.79 eV (8.43 Å²/eV); under the 0.35 V/Å, 8 fs pulse convention the invariant amplitude peak is 2.427 Å at 5.79 eV (largest single mode 1.195 Å). First non-zero response at 1.17 eV. Between the last two meshes (k48 → k64) the 0.10 eV envelope changes by 1.46 % (limit 3 %; raw spectrum 11.2 %), so the kernel is converged on the envelope.

Scope: Γc only (no Γe vertex correction), scalar-relativistic, PBE gap, Gamma-only DFPT (one q-point, `ldisp = .true.`, `nq = 1 1 1`); velocities from EPW's `vme = 'dipole'` route (the full velocity i[H,r], non-local pseudopotential commutator included, computed on the coarse mesh and Wannier-interpolated; origin-free).

## Standard all-mode result (64×64×64)

![CdS_mp672_e2eH all optical modes and all tensor directions, unified scale](figures/cds_mp672_e2eh_all_modes_k64_sharey.png)

![CdS_mp672_e2eH all optical modes, per-panel scale](figures/cds_mp672_e2eh_all_modes_k64.png)

![CdS_mp672_e2eH mode-channel peak heatmap](figures/cds_mp672_e2eh_mode_channel_heatmap_k64.png)

![CdS_mp672_e2eH optical-mode invariant and channel resolution](figures/cds_mp672_e2eh_invariant_k64.png)

| Quantity (64×64×64, 0.03 eV smearing, 300 K) | Value |
|---|---|
| Invariant \|Γ\| peak | 8.43 Å²/eV at 5.79 eV |
| Envelope (0.10 eV) peak | 5.94 Å²/eV at 5.76 eV |
| Invariant amplitude peak (0.35 V/Å, 8 fs) | 2.427 Å at 5.79 eV |
| Per-mode amplitude peaks (basis-dependent split) | 1.194 / 1.195 / 0.016 / 0.435 / 0.122 / 0.121 / 0.221 / 0.221 / 0.019 Å |
| Mode-summed channel peaks, diagonal (xx, yy, zz) | 1.97–4.44 Å²/eV |
| Mode-summed channel peaks, off-diagonal (xy, xz, yz, yx, zx, zy) | 0.90–3.97 Å²/eV |
| Diagonal / off-diagonal peak ratio | 1.118 |
| First non-zero response | 1.17 eV |
| Photon grid | 0.03–6.00 eV, 200 points |

## Electronic structure and Wannier state

| Quantity | Value |
|---|---|
| PBE band edges (VBM / CBM) | 7.068 / 8.309 eV (gap 1.241 eV) |
| Consumer shell (must be interpolated well) | 2.01 … 13.37 eV |
| Frozen / outer window | 2.59 … 15.37 eV / 2.59 … 22.79 eV |
| Wannier functions | 18 (Cd:s, S:p;d); recipe source: casebook |
| Accepted Wannier round | round 1 (1 round gate on file, including any before an electron recompute); max spread 4.63 Å², band RMS 2.6 meV, worst 15.1 meV in the shell (limits 10 Å², 50 / 25 meV) |
| EPW-side interpolation (same shell, from the EPW1 Wannier files) | RMS 2.6 meV, worst 14.9 meV → PASS |

![CdS_mp672_e2eH DFT bands versus the Wannier interpolation, with the shell and windows](figures/cds_mp672_e2eh_bands_dft_vs_wannier.png)

## Γ-point phonons (DFPT)

| Mode | ω (cm⁻¹) | ω (meV) |
|---|---:|---:|
| optical 4 | 39.17 | 4.86 |
| optical 5 | 39.17 | 4.86 |
| optical 6 | 134.94 | 16.73 |
| optical 7 | 234.50 | 29.07 |
| optical 8 | 241.96 | 30.00 |
| optical 9 | 241.96 | 30.00 |
| optical 10 | 255.54 | 31.68 |
| optical 11 | 255.54 | 31.68 |
| optical 12 | 302.32 | 37.48 |

Acoustic sum rule applied (dynmat.x); acoustic modes after ASR -0.00, 0.00, 0.00 cm⁻¹ (raw 6.31, 8.13, 8.13 cm⁻¹). ε∞ diagonal 6.13, 6.13, 6.22; largest |Z*| 2.20; polar: True. Gate: PASS. Softness: soft (tier 1).

## Tier 1: anharmonic Γ phonons

Classified **soft** at the phonon gate (lowest optical mode 39.17 cm⁻¹, threshold 60 cm⁻¹); so the tier-1 stage ran: supercell force sets, least-squares force constants (Pheasy and ALAMODE), self-consistent renormalisation at 0, 100, 300 K, and the renormalised Γ dynamical matrix at 300 K injected into a second EPW run (rekernel).

Lattice check (the same DFPT at the PBE cell; the production cell is the cell policy's):

| optical mode | production cell (cm⁻¹) | PBE cell (cm⁻¹) | shift |
|---|---:|---:|---:|
| 4 | 39.17 | 44.22 | -5.05 |
| 5 | 39.17 | 44.22 | -5.05 |
| 6 | 134.94 | 129.59 | +5.35 |
| 7 | 234.50 | 213.76 | +20.74 |
| 8 | 241.96 | 221.32 | +20.64 |
| 9 | 241.96 | 221.32 | +20.64 |
| 10 | 255.54 | 233.43 | +22.11 |
| 11 | 255.54 | 233.43 | +22.11 |
| 12 | 302.32 | 282.05 | +20.27 |

Force sets: anh: 8 configurations of 32 atoms at 0.04 Å (supercell 2x2x2, mesh 4x4x3, estimate 1.55 node-h); harm: 4 configurations of 32 atoms at 0.01 Å (supercell 2x2x2, mesh 4x4x3, estimate 0.78 node-h).

Fits (Pheasy, least squares, long-range part kept): harmonic RMSE 0.0015 eV/Å (2.8 %), orders 2–4 jointly RMSE 0.0012 eV/Å (0.6 %). Harmonic gate against the DFPT Γ modes (production fc2 of the adopted joint fit (T3, v2.0.9)): largest deviation 1.89 cm⁻¹ (limit 2 cm⁻¹ or 1 % per mode) → PASS. Harmonic reference set (report only): largest deviation 4.21 cm⁻¹.

Cubic/quartic cutoff ladder (the first cutoff whose quartic surface passes the trust gate is adopted): 4.0 Å (84 terms): trusted. Adopted 4.0 Å.

Renormalised optical Γ modes (cm⁻¹; ALAMODE SCPH loop on the 4x4x4 inner mesh; Pheasy SCP loop in brackets):

| mode | harmonic (DFPT) | 0 K | 50 K | 100 K | 150 K | 200 K | 250 K | 300 K |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 39.17 | 40.6 (41.1) | 42.0 | 44.6 (46.0) | 46.9 | 49.2 | 51.2 | 53.4 (54.4) |
| 5 | 39.17 | 40.6 (41.1) | 42.0 | 44.6 (46.0) | 46.9 | 49.2 | 51.2 | 53.4 (54.4) |
| 6 | 134.94 | 135.1 (135.0) | 135.2 | 135.4 (135.0) | 135.6 | 135.8 | 136.0 | 136.2 (135.5) |
| 7 | 234.50 | 235.3 (235.1) | 235.3 | 235.3 (234.5) | 235.5 | 235.8 | 236.1 | 236.5 (235.0) |
| 8 | 241.96 | 243.1 (243.3) | 242.5 | 241.6 (242.4) | 240.7 | 239.8 | 238.9 | 238.1 (239.5) |
| 9 | 241.96 | 243.1 (243.3) | 242.5 | 241.6 (242.4) | 240.7 | 239.8 | 238.9 | 238.1 (239.5) |
| 10 | 255.54 | 255.3 (255.4) | 254.6 | 253.3 (253.8) | 252.0 | 250.7 | 249.4 | 248.2 (249.4) |
| 11 | 255.54 | 255.3 (255.4) | 254.6 | 253.3 (253.8) | 252.0 | 250.7 | 249.4 | 248.2 (249.4) |
| 12 | 302.32 | 304.1 (304.0) | 304.1 | 304.0 (303.5) | 304.0 | 304.2 | 304.3 | 304.5 (303.7) |

Solver agreement on the softest mode at 300 K: 1.1 cm⁻¹ (limit 10); ALAMODE converged at the gate temperatures: True; real at every converged temperature: True.

Three-phonon full widths at Γ on the renormalised constants (phono3py, 8x8x8 mesh, cm⁻¹):

| mode | 100 K | 300 K |
|---|---:|---:|
| 4 (54.4 cm⁻¹) | 0.07 | 0.22 |
| 5 (54.4 cm⁻¹) | 0.07 | 0.22 |
| 6 (135.5 cm⁻¹) | 0.15 | 0.60 |
| 7 (235.0 cm⁻¹) | 2.06 | 7.07 |
| 8 (239.5 cm⁻¹) | 1.55 | 5.22 |
| 9 (239.5 cm⁻¹) | 1.55 | 5.22 |
| 10 (249.4 cm⁻¹) | 1.12 | 3.83 |
| 11 (249.4 cm⁻¹) | 1.12 | 3.83 |
| 12 (303.7 cm⁻¹) | 1.49 | 3.99 |

Renormalised kernel: EPW re-run on the injected Γ dynamical matrix (300 K) at mesh k64; result `results/rekernel_k64/Gamma_alphabeta_s.dat`.
Against the harmonic kernel at the same mesh: envelope difference 8.15 % (the ladder's own metric; its acceptance limit is 3 %), raw peak 8.43 → 7.37 Å²/eV at 5.79 eV. A small difference on a stiff crystal is the expected outcome; on a soft-mode material this line carries the anharmonic correction of the kernel.

## Velocity-route check

Wannier centres sit up to 6.97 Å from the cell origin (b·r max 1.31); EPW's `wannier` velocity route would carry an origin-dependent error of about 28 % at worst (15.5 % on average) for this cell — above the warning level.

| Adopted mesh | Production route | Other route | Envelope difference | Tensor difference | Invariant peak (production / other) | Forbidden-channel ratio (production / other) | Verdict |
|---|---|---|---:|---:|---|---|---|
| k64 | dipole | wannier | 1.5 % (limit 5 %) | 16.0 % | 8.43 / 8.32 Å²/eV | 1.118 / 1.112 | PASS |

Reading: the two velocity routes agree.

## Fine-k convergence

Convergence is judged on the 0.10 eV Gaussian envelope of the invariant (gate: consecutive rel-L2 <= 0.03); the raw rel-L2 is reported, not gated.

| Meshes | raw rel-L2 | raw Pearson | envelope rel-L2 | envelope peak | gate |
|---|---:|---:|---:|---|---|
| 40×40×40 → 48×48×48 | 0.161 | 0.974 | 0.022 | 5.96 → 5.95 Å²/eV, 5.76 → 5.76 eV | PASS |
| 48×48×48 → 64×64×64 | 0.112 | 0.987 | 0.015 | 5.95 → 5.94 Å²/eV, 5.76 → 5.76 eV | PASS |

![CdS_mp672_e2eH fine-k convergence](figures/kmesh_convergence.png)

Per-mesh overlay of the raw invariant, its envelope, and the change between consecutive meshes (the top 0.2 eV of the window is excluded from the gate):

![CdS_mp672_e2eH per-mesh overlay](figures/kmesh_overlay.png)

## What was done

1. **intake**: ACCEPTED — CdS sg 186 nbnd 65
2. **relax**: ACCEPTED, job 22861412 (debug, COMPLETED) — max force 2.271e-05 Ry/bohr, pressure -0.34 kbar
3. **electron**: ACCEPTED, job 22861698 (debug, COMPLETED) — gap 1.241 eV; PDOS 5 shells; trim: 20 bands excluded (gap 2.141 eV); v1.1 recipe from the superset stage
4. **wannier**: ACCEPTED, job 22862731 (small, COMPLETED) — round 1: score 0.192 <= 0.9 (W7); wout_present=ok; final_state=ok; num_wann_in_wout=ok; spread_max=ok; plateau_drift=ok; localisation_converged=ok; ran_out_of_steps=ok; all_done=ok; disentanglement_settled=ok; comparison_present=ok; comparator_build=ok; dense_reference_certified=ok; band_rms_meV=ok; band_worst_meV=ok; grids_equal=ok
5. **phonon**: ACCEPTED, job 22862063 (debug, COMPLETED) — max 302.32 cm-1; polar=True; softness soft -> tier 1
6. **epw1**: ACCEPTED, job 22863435 (small, COMPLETED) — restart written; EPW bands within the shell bars
7. **kernel**: ACCEPTED, job 22871330 (small, COMPLETED) — converged at k64: envelope change 0.0146 <= 0.03 with previous 0.0220 <= 0.1; velocity-route check PASS (envelope 1.5 %, tensor 16.0 %)
8. **report**: PENDING
9. **anharmonic**: ACCEPTED, job 22867403 (small, COMPLETED) — tier 1 done: softest mode 0 K: 40.6, 100 K: 44.6, 150 K: 46.9, 200 K: 49.2, 250 K: 51.2, 300 K: 53.4, 50 K: 42.0 cm-1
10. **rekernel**: ACCEPTED, job 22876187 (small, COMPLETED) — renormalised kernel at k64 (300 K)
11. **superset**: ACCEPTED, job 22862056 (small, COMPLETED) — superset 36 functions; round-1 recipe casebook (CdS_mp672_kp): 18 functions (reduced), Pmin 14

Wannier recipe (round 1, source casebook: CdS_mp672_kp): 18 functions, projections ['Cd:s', 'S:p;d'], exclude_bands [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], outer window [2.5947, 22.7901] eV, frozen window [2.5947, 15.368] eV, consumer shell [2.009, 13.368] eV.

Electronic policy: ecutwfc 102 Ry, ecutrho 408 Ry, SCF mesh [9, 9, 5], NSCF mesh [9, 9, 5], nbnd 65, relax `fixed`, spacegroup P6_3mc (186), nat 4.

## Validation gates

| Gate file | Status | Key numbers | Reasons |
|---|---|---|---|
| `gate_anharmonic_analysis` | PASS | — | — |
| `gate_anharmonic_anh` | PASS | — | — |
| `gate_anharmonic_harm` | PASS | — | — |
| `gate_anharmonic_lattice_check` | PASS | — | — |
| `gate_electron` | PASS | — | — |
| `gate_epw1` | PASS | — | — |
| `gate_kernel_k40` | PASS | — | — |
| `gate_kernel_k48` | PASS | — | — |
| `gate_kernel_k64` | PASS | — | — |
| `gate_kernel_k64_eta030` | PASS | — | — |
| `gate_phonon` | PASS | optical_max_cm1 302.3; acoustic_cm1_asr [-0.0, 0.0, 0.0]; max_abs_zstar 2.204; polar True | — |
| `gate_rekernel_epw1` | PASS | — | — |
| `gate_rekernel_k64` | PASS | — | — |
| `gate_relax` | PASS | — | — |
| `gate_route_check` | PASS | — | — |
| `gate_superset` | PASS | — | — |
| `gate_wannier_round1` | PASS | — | — |

Standing limits: Wannier spreads <= 10 Å², band RMS <= 50 meV and worst <= 25 meV in the consumer shell, Γ acoustic modes within 1 cm⁻¹ after ASR, envelope rel-L2 <= 0.03.

## Scope, limits, and next safe action

- **Γc only.** The triangle term Γc is computed; the vertex correction Γe is absent.
- **Scalar-relativistic, PBE gap.** No spin-orbit coupling and no gap correction; the onset follows the PBE gap, so absolute peak positions cannot be compared with experiment without a scissor.
- **Gamma-only DFPT.** Phonons are computed at q = 0 only; the LO–TO splitting is not resolved at exactly Γ and no off-Γ stability check exists in this route.
- **Forbidden-channel residual.** Diagonal / off-diagonal mode-summed peak ratio 1.118; which channels are symmetry-forbidden depends on the point group and must be judged for this material.
- **Convergence.** Envelope rel-L2 0.0146 and raw rel-L2 0.112 between 48×48×48 and 64×64×64.

## Run record

- Workflow baseline at creation: v2.0.12 (sealed 2026-10-15, manifest `e8050e6a9f5b…`, tree clean)
- Cell policy: pbesol (cell relaxed with PBEsol, internal coordinates and every later stage with PBE); production cell: input
- Phonon tier: 1 (softness soft, lowest optical mode 39.17 cm⁻¹, threshold 60.0 cm⁻¹)
- Material workflow dir: `<cophon>/benchmarks/cophon-bench-v1/e2e_library/CdS_mp672_e2eH`
- LUMI run root: `/scratch/project_<id>/<user>/theory2code/cphon/runs/CdS_mp672_e2eH/wf`
- Job ledger: `JOB_LEDGER.md` (one row per submitted job)
- Jobs: anharmonic 22867403 (small, COMPLETED); electron 22861698 (debug, COMPLETED); epw1 22863435 (small, COMPLETED); kernel 22871330 (small, COMPLETED); phonon 22862063 (debug, COMPLETED); rekernel 22876187 (small, COMPLETED); relax 22861412 (debug, COMPLETED); superset 22862056 (small, COMPLETED); wannier 22862731 (small, COMPLETED)
- Kernel files (SHA-256): k40 `d6b80baf295a…`; k48 `510a2f823d90…`; k64 `58bc417a17ed…`
- 2026-10-15T14:05:46+02:00: kernel:COLLECTED — k64_eta030: 51 files pulled
- 2026-10-15T14:05:46+02:00: kernel:ACCEPTED — converged at k64: envelope change 0.0146 <= 0.03 with previous 0.0220 <= 0.1; velocity-route check PASS (envelope 1.5 %, tensor 16.0 %)
- 2026-10-15T14:05:48+02:00: ROUTE — rekernel_epw1: small — estimated start in 2.7 h; standard 17.9 h; small 2.69 h
- 2026-10-15T14:05:52+02:00: rekernel:SUBMIT — job 22872846 on small in /scratch/project_<id>/<user>/theory2code/cphon/runs/CdS_mp672_e2eH/wf/rekernel/epw1
- 2026-10-15T16:27:16+02:00: rekernel:COLLECTED — epw1: 13 files pulled
- 2026-10-15T16:27:16+02:00: rekernel:PENDING — renormalised EPW1 done; kernel next
- 2026-10-15T16:27:18+02:00: ROUTE — rekernel_kernel: small — estimated start in 0.7 h; standard 21.03 h; small 0.68 h
- 2026-10-15T16:27:22+02:00: rekernel:SUBMIT — job 22876187 on small in /scratch/project_<id>/<user>/theory2code/cphon/runs/CdS_mp672_e2eH/wf/rekernel/kernel
- 2026-10-15T17:00:53+02:00: rekernel:COLLECTED — kernel: 21 files pulled
- 2026-10-15T17:00:53+02:00: rekernel:ACCEPTED — renormalised kernel at k64 (300 K)
