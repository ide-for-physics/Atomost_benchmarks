# Atomost benchmarks

Benchmarks of Atomost's harness-level AI development systems for materials computation, and of atomost, the governance layer the team runs its agent sessions through. Each benchmark is a folder with a
human-facing report, the figures and the grading tables it is built from, the design documents and the deliverables of every arm that
was compared. For the harness benchmarks, labels and graders are frozen before any run; grades are produced by the pipeline's own code
gates, never by a model judge. The experiment benchmarks check the physics the pipeline computes against published measurements.

| Benchmark | Date | What it measures | Report |
|---|---|---|---|
| [cophon-bench v0](cophon-bench-v0/) | 2026-10-15 (v0.1) | the coherent-phonon kernel pipeline as a harness: the same model inside vs on a whiteboard, and whether the harness lifts the cheapest model to the level of the strongest one working alone | [中文报告](cophon-bench-v0/report/REPORT.md) · [English summary](cophon-bench-v0/report/SUMMARY.en.md) |
| [experiment benchmarks](experiment-benchmarks/) | 2026-08-31 to 2026-10-11 (round 1) | the theory itself: under the same material and pump conditions as published experiments on NbOI₂, monolayer MoS₂ and InP, does the computed kernel predict which mode is driven, along which axis it radiates and where the driving peaks; new predictions on record for experiments not yet done | [README](experiment-benchmarks/README.md) |
| [atomost-bench v0](atomost-bench-v0/) | 2026-10-17 | atomost, the layer every agent session of the team starts through: does a fresh session follow the team's rules with no memory, the pre-atomost native memory, or the curated atomost memory home (43 frozen items, Haiku 5.5 and Opus 5.5, 774 runs); replays of strategist wake policies and of the console's failure alerts | [English summary](atomost-bench-v0/report/SUMMARY.en.md) · [中文报告](atomost-bench-v0/report/REPORT.md) |

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

Experiment benchmarks: published are the comparison reports, figures, scripts and metrics, and two small data tables taken from papers
(seven points digitised from Trovatello et al. 2020; the public-domain InP optical constants of Aspnes & Studna 1983), each with its
citation. Not published: the papers and other third-party files (cited by DOI or arXiv number instead), and the kernel files and phonon
data the scripts read.

## atomost-bench v0 in one paragraph

The same model started in a project folder with three different memories: a cheap model (Haiku 5.5) follows the team's rules 76% of the time with no memory and 93–97% with project memory; the curated atomost memory answers with 26–28% fewer tokens than the uncurated native one; a memory that mixes every project's rules costs more than no memory at all ($0.174 vs $0.110 per answer, $0.080 with the atomost home, all at 100% correct). atomost does not make answers more accurate: the strong model (Opus 5.5) scores 97% with no memory by searching the project files. Strategist sessions woken on change cost $49 over 10 days against about $996 for an hourly round (replay). Details and every gap: [atomost-bench-v0/report/SUMMARY.en.md](atomost-bench-v0/report/SUMMARY.en.md).

## 中文

这是 Atomost 的 harness 级 AI 研发系统的能力基准。每个基准一个目录：人文报告、图、判分表、设计文件、每一臂的交付件。标签与判分器在任何
运行之前冻结，判分只用流水线自己的代码门。cophon-bench v0 的报告见 `cophon-bench-v0/report/REPORT.md`，它证明了什么、没证明什么都在报告的
附录 A。atomost-bench v0 测的是团队所有 AI 会话都经过的治理层 atomost（项目记忆家、参谋会话、记账、手机提醒），报告见
`atomost-bench-v0/report/REPORT.md`。experiment-benchmarks/ 是另一类：检验理论本身，在和已发表实验相同的材料与泵浦条件下，算出的结果能不能预言实验测到的东西，
并写下了等待实验检验的新预测。

© Atomost. All rights reserved; contact the maintainers for reuse.
