# cophon-bench v1 — summary in English

Version v1.0.1 (2026-10-18: the v1.0 close-out, published the same day). The full report is in Chinese: `REPORT.md`. All numbers come from the frozen graders' tables in
`../tables/`; the figures are generated from those tables by `cophon_bench/figures_v1.py`.

## What changed from v0

v0 (2026-10-15) asked two questions of the cophon harness (sealed pipeline + gates + rulebook + prior + supervisor + ticket contract
with an operator model): does the same model do better inside the harness than on a whiteboard, and does the harness lift the cheapest
model to the level of the strongest model working alone? v1 replaces v0's inferences with measurements:

- **E end to end:** 8 materials (GaP, SnS2, NbFeSb, CdS, KNbO3, InPS4, Bi2O2Se, MoS2 monolayer) × 4 arms (harness + Haiku 5.5,
  harness + Fable 5.1, whiteboard Haiku, whiteboard Fable); cells sealed into the task; grading by a top-two-peak rule (the arm's
  highest peak within ±0.15 eV of one of the baseline's two highest peaks, height ±25 %, driven mode ±5 %).
- **A operator tickets:** the 44 v0 tickets plus 7 hold-out tickets raised after the v0 freeze; 5 repeats instead of 3.
- **C batch selection:** 10 materials drawn at random (stratified by chemistry) from the 78 the loop had scored but not computed were
  computed (46.9 node-h), growing the pool to 47.
- **B Wannier projection:** a third round was answered (137 answers) but **not graded**: grading runs wannier90 jobs on LUMI.

v1 was not run to the end. LUMI closed on 2026-10-17 14:00 for security reasons with no reopening date; the owner decided on
2026-10-18 to finish everything that did not need LUMI and close v1. Missing as a result: whiteboard Fable on InPS4 (first run invalid,
see below; rerun never started), whiteboard Fable on Bi2O2Se (stopped at its own provisional 64³ answer), and B round 3 grading.

![F1](figures/F1_overview.png)

## Results

- **A.** On the 44 main tickets (median of 5) the harness arm scores 35.75–38.25 for all five models and the whiteboard arm
  27.25–31.75; "escalate everything" scores 32.5. The same model gains 6.5–9.75 points in the harness. Whiteboard models waste compute
  on 4–7 tickets each, harness models on none. Harness + Haiku (35.75) beats every whiteboard model (best: Opus 31.75). On the 19 tickets
  that need a real decision the medians are identical to v0: frontier models are equally good on both arms (Fable 14 / 14, Opus
  14 / 14). On the **7 hold-out tickets** every model again scores higher in the harness (harness 5.5–7.0, whiteboard 3.75–6.0,
  escalate-everything 4.0; harness + Haiku 6.5 vs whiteboard Fable 5.5). Most of that gap is half points (explain vs. wait on two
  nothing-is-wrong tickets); seven tickets is a small set.
- **C.** On the 33 materials the loop itself found or drew (the models cannot recall them), all five harness models hit 4 of 8
  (line-hit and radiating), whiteboard models 0–1; random 2.42, the prior alone 5, best possible 6. Whiteboard models spend most picks on
  famous materials outside this pool (KNbO3, BaTiO3, LiNbO3). On the whole pool of 47, frontier models tie on "promising" picks (3 vs 3).
  The harness's edge in C is mostly its prior; only Fable and Opus add the one promising loop-found material (LiAsS2). The 10 random
  additions hold 1 line-hit material and no promising one, against 9 line-hits among the 23 materials the loop had chosen.
- **E.** Of the 11 harness arms that finished, all 11 give the same answer as the sealed baseline; of the 14 counted whiteboard arms that
  finished, 10 do. Both whiteboard models are wrong on CdS (kernel 47× too high: an SCF/NSCF FFT-grid mismatch that the harness rulebook
  records as a rule, found on the same material on 2026-10-02) and on KNbO3 (three near-equal peaks; the rule picks a different top
  peak although whiteboard Fable's spectrum is the closest to the baseline). **But 5 of the 16 harness arms did not finish**, all stopped
  at Wannier-related gates (4 at an EPW-vs-wannier90 spread consistency gate, 1 out of Wannier rounds); no whiteboard arm got stuck. On
  the 5 materials all four arms finished, harness + Haiku used 12.6 node-h and $0.09 of model spend, whiteboard Haiku 17.1 node-h and
  $16, whiteboard Fable 24.1 node-h and $122. Whiteboard Haiku, not tested in v0, finished all 8 materials with 6 correct at one seventh
  of whiteboard Fable's spend.

![F4](figures/F4_E_kernels.png)

**Verdict.** Question 1 holds on A (including the hold-out tickets), holds on C for the loop-found materials and partly on the whole
pool, and holds only partly on E: the harness is right whenever it finishes and cheaper on the materials everyone finished, but it failed
to finish 5 of 16 arms. Question 2 holds on A, partly on C, and on E in a narrower sense than v0 claimed: the harness gives a cheap model
correctness (CdS), low spend and a reproducible process, not the difference between doing and not doing, since whiteboard Haiku also
finished all eight. v0's "3.6× less compute end to end" shrinks in v1 to 0.5–0.75× on the materials all arms finished, and to no saving
once the unfinished harness arms are counted.

## Disclosures

- InPS4 whiteboard Fable is invalid: the task template gave both whiteboard arms of a material the same remote directory, and the Fable
  arm, resuming after a subscription limit, continued from the Haiku arm's calculations (18 of its 20 jobs were Haiku's). Graded apart,
  not counted. Bi2O2Se whiteboard Fable's provisional answer grades "same" but is not counted either (it never declared itself done).
- The two Bi2O2Se harness arms used ~23 node-h each, beyond the design's 10 node-h per material cap, which the benchmark did not
  enforce during the run.
- Whiteboard node-hours are self-reported from each arm's job log; with LUMI closed they could not be cross-checked with sacct.
- Harness defects found during the run went to line 2 as a handoff (`records/handoffs/2026-10-15-bench-v1-harness-findings-for-line2.md`);
  the benchmark did not modify the harness.

## Cost

1417 offline model answers (A 1230, B round 3 137, C stage 2 50), 94 ticket-relay calls, 16 whiteboard arms. $694 at list price
(A $298, B $53, C $30, E relay $37, whiteboard arms $276; Fable $544 of it). 204.8 node-hours (E harness 81.4, E whiteboard 76.4
self-reported, C expansion 46.9, first harness attempts 0.1). Details: `../tables/COSTS.md`.
