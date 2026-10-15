# cophon-bench v0 — summary in English

Version v0.1 (first checkpoint, 2026-10-15). The full report is in Chinese: `REPORT.md`. All numbers come from the frozen grading
tables in `../tables/`; the figures are generated from those tables by `cophon_bench/figures_v0.py`.

## What was measured

cophon is Atomost's pipeline that takes a crystal structure to its light-induced coherent-phonon generation kernel Γ(ω), the quantity
that says which photon energy drives which phonon how strongly in a candidate terahertz-source material. The pipeline is a *harness*: sealed
code with a gate after every stage, a rulebook, recipe strategies, a casebook of certified recipes, a cheap prior over 193 materials,
a supervisor that runs the routine unattended, and a ticket contract through which an operator model is asked for judgment only when a
stage blocks. The model inside can be anything; this benchmark used Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1 and DeepSeek v4 flash.

Two questions, five tasks. Question 1: does the same model do better inside the harness than on a whiteboard (structure, papers,
toolchain and cluster, nothing else)? Question 2: does the harness lift the cheapest model to the level of the strongest model working
alone? Labels and graders were frozen before any whiteboard run; every grade is produced by the pipeline's own gates, never by a model
judge; every answer was repeated three times and the median taken.

| Task | Question | Pool | Grader | Compute |
|---|---|---|---|---|
| A operator tickets | the pipeline is blocked, what next | 44 real tickets | frozen best / acceptable / wrong action sets | 0 |
| B Wannier projection | choose the projection block from the projectability evidence | 16 materials | wannier90 run, pipeline gate (score ≤ 0.9, spreads ≤ 10 Å²) | 332 blocks, 35.8 node-h |
| C batch selection | pick 8 likely THz sources | 37 materials with sealed kernels | Screening Baseline v2 (definition v2.1) | 0 |
| D peak prediction | photon energy of the kernel peak and the driven mode | 37 materials | ±0.3 eV, shortlist of 3, mode ±10 % | 0 |
| E end to end | structure to kernel, unattended | GaP, SnS2, NbFeSb | peak ±0.15 eV, height ±25 %, same mode; node-hours from sacct | 39 node-h |

![F1](figures/F1_overview.png)

## Results

- **A.** Inside the harness all five models score 35.75–38.75 of 44 with zero compute-wasting answers; on the whiteboard they score
  28.5–31.75 with 4–7 wasteful resubmissions each. Harness + Haiku (36.25) beats whiteboard Fable (28.5). On the 19 tickets that need a
  real decision the frontier models are as good on the whiteboard as in the harness (14 vs 14); the harness's value here is boundaries,
  legality and zero waste, and lifting Haiku and Sonnet.
- **B.** The harness's code recipe passes 13 of 16 materials at round 1 with no model. The best whiteboard models pass 9 at round 1 and
  11–12 after a second round with their own scores fed back; Haiku passes 7 on the whiteboard and 14 inside the harness. No whiteboard
  model passed NbFeSb; with the diagnosis card only Sonnet did, once in three.
- **C.** On the 23 materials the active-learning loop itself discovered (which the models cannot recall), whiteboard Fable hits 2 of 8,
  harness + Haiku 4, harness + Fable 5; random 3.1, the prior alone 5, the best possible 7. The pool is prior-biased (see gaps).
- **D.** Small gain: 1–3 more materials within 0.3 eV, median error 1.0 → 0.7 eV. Frontier models on the whiteboard already match the
  pipeline's prior locator.
- **E.** All three materials: whiteboard Fable reached the same physics (height and mode on all three; GaP and NbFeSb the same answer by the
  rule). Harness + Haiku: 8.4 node-hours, $3.4 of model spend, zero errors, zero owner decisions; whiteboard Fable: 30.4 node-hours, $98,
  321 turns. The NbFeSb harness kernel equals the same-day production flight to the last digit. Wall-clock was *not* a harness win (9–11 h
  vs 4–10 h): the pipeline's EPW job queued 7.5 h on the standard partition. SnS2's peak position differed across the three runs because
  three different cells were used (measured, PBEsol-relaxed, Materials Project as given); height and mode agreed.

![F7](figures/F7_E_kernels.png)

## What v0 does not show (appendix A of the report)

![F9](figures/F9_capability_map.png)

Not shown: faster wall-clock; batch selection beyond a prior-biased pool (1 promising material among the 23); kernel-peak prediction from
cheap data (the locator is weak); a model solving the hardest Wannier case from the diagnosis card; a separate harness + Fable end-to-end
arm (inferred equivalent, not measured); generalisation beyond one pipeline, one lab, n = 3 repeats; agreement with experiment (the
benchmark grades against sealed answers, not measurements). Harness defects found: a silent fallback to the PBEsol cell when the
measured-cell lookup fails; a packed Slurm step that hangs to the wall clock when its launch fails; an under-estimated wall time for
full-mode Wannier tasks; single-maximum grading of two-peak spectra; the headless runner accepting a "session limit" reply as an answer
(guarded after the freeze, disclosed in `FREEZE_NOTE.md`).

## Cost

1856 model answers, $519 at list price (A $314, B $145, C/D $56, E relay $3.4) plus $98.3 for the three whiteboard sessions; 74.6 node-hours
on LUMI (B 35.8, E harness 8.4, E whiteboard 30.4).
