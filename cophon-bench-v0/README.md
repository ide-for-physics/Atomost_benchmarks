# cophon-bench v0 (v0.1, 2026-10-15)

| Folder | What |
|---|---|
| `report/` | `REPORT.md` (Chinese, the human-facing report with nine figures and the gap appendix), `SUMMARY.en.md`, `figures/` |
| `tables/` | the frozen grading tables: `A_table.md`, `A_best.md`, `B_table.md`, `B_cumulative_r2.json`, `C_table.md`, `D_table.md`, and the per-answer detail JSON of each pillar |
| `design/` | `E_DESIGN.md` (end-to-end design), `FREEZE_NOTE.md` (what changed after the freeze and why), the checkpoint freeze list, `wb_audit.py` (the isolation audit of the whiteboard sessions) |
| `e2e/` | end to end: `E_TIMELINE.log`; `harness_<M>/` the harness arm's pipeline report, job ledger, cost, gate files and standard figures; `whiteboard_<M>/` the whiteboard arm's task sheet, notes, report, job log, graded kernel files, Wannier re-grade, inputs and scripts |

Materials of the end-to-end task: GaP (mp-2490), SnS2 (mp-1170), NbFeSb (mp-9437). Baselines (sealed before the runs): GaP 2.82 eV / 16.0 Å²/eV /
T2 10.77 THz; SnS2 5.46 / 47.1 / A1g 9.35 THz; NbFeSb 3.36 / 21.3 / T2 8.26 THz.

Reading order: `report/SUMMARY.en.md` or `report/REPORT.md`, then `tables/`, then the arm deliverables under `e2e/`.
