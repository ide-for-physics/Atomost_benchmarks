# Atomost benchmarks

Benchmarks of Atomost's harness-level AI development systems for materials computation. Each benchmark is a folder with a
human-facing report, the figures and the grading tables it is built from, the design documents and the deliverables of every arm that
was compared. Labels and graders are frozen before any run; grades are produced by the pipeline's own code gates, never by a model judge.

| Benchmark | Date | What it measures | Report |
|---|---|---|---|
| [cophon-bench v0](cophon-bench-v0/) | 2026-10-15 (v0.1) | the coherent-phonon kernel pipeline as a harness: the same model inside vs on a whiteboard, and whether the harness lifts the cheapest model to the level of the strongest one working alone | [中文报告](cophon-bench-v0/report/REPORT.md) · [English summary](cophon-bench-v0/report/SUMMARY.en.md) |

## cophon-bench v0 in one figure

![overview](cophon-bench-v0/report/figures/F1_overview.png)

Five tasks (A operator tickets, B Wannier projection, C batch selection, D kernel-peak prediction, E end to end), five models (Haiku 5.5,
Sonnet 5.5, Opus 5.5, Fable 5.1, DeepSeek v4 flash), 1856 model answers, 75 node-hours on LUMI. Inside the harness the cheapest model
beats the strongest model working alone on operations (36.25 vs 28.5 of 44) and on the Wannier step (14 vs 11 of 16 materials), and
reaches the same end-to-end physics with 3.6× less compute and 30× less model spend. Wall-clock, batch selection beyond a biased pool
and peak prediction from cheap data are *not* shown; the report's appendix A lists every gap and every harness defect the benchmark found.

## What is and is not in this repository

Published: reports, figures, grading tables (with per-answer detail), the end-to-end design, the freeze note and checkpoint freeze list,
the end-to-end timeline, the harness arm's per-material reports / gates / figures / cost, the whiteboard arm's task sheets, notes, reports,
job logs, inputs and graded kernel files, the isolation-audit script.

Held privately (available for diligence on request): the harness's prompts and ticket texts, the frozen labels, the pipeline code
(kernel_pipeline), raw model answers, the whiteboard sessions' full transcripts, the raw wannier90 outputs of pillar B. Cluster project
ids, user names and local paths are scrubbed from the published text.

## 中文

这是 Atomost 的 harness 级 AI 研发系统的能力基准。每个基准一个目录：人文报告、图、判分表、设计文件、每一臂的交付件。标签与判分器在任何
运行之前冻结，判分只用流水线自己的代码门。cophon-bench v0 的报告见 `cophon-bench-v0/report/REPORT.md`，它证明了什么、没证明什么都在报告的
附录 A。

© Atomost. All rights reserved; contact the maintainers for reuse.
