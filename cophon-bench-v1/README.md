# cophon-bench v1 (v1.0.1, 2026-10-18)

The second version of the cophon harness benchmark. The harness is the coherent-phonon kernel pipeline as the team runs it: a sealed
first-principles pipeline (Quantum ESPRESSO, wannier90, the authors' EPW variant) with code gates after every stage, a rulebook of
past failures, a prior for choosing materials, a supervisor and a ticket contract with an operator model. v1 asks the same two questions
as v0 (does the same model do better inside the harness than working alone; does the harness lift a cheap model to the level of a
frontier one) and replaces v0's inferences with measurements: end to end on 8 materials with four arms each, 7 operator tickets raised
after the v0 freeze, a selection pool grown by 10 randomly drawn and newly computed materials, 5 repeats of every offline answer.

LUMI closed on 2026-10-17 before v1 finished. Missing as a result: whiteboard Fable on InPS4 (first run invalid) and on Bi2O2Se
(stopped at its own provisional answer), and the grading of the third round of the Wannier task.

Reading order: `report/SUMMARY.en.md` or `report/REPORT.md` (Chinese, five figures, appendix A lists what v1 does not show), then
`tables/`, then the arm deliverables under `e2e/`.

| Folder | What |
|---|---|
| `report/` | `REPORT.md`, `SUMMARY.en.md`, `figures/` |
| `tables/` | the frozen graders' tables: `A_table.md` with per-answer `A_detail.json` (operator tickets, main set and hold-out set), `C2_table.md` with `C2_detail.json` (batch selection, pool of 47), `E_table.md`, `E_table_excluded.md` and `E_ledger.md/.json` (end to end, per arm), `COSTS.md/.json` |
| `design/` | `DESIGN.md` (Chinese), `FREEZE_NOTE.md` (every change after the freeze and why), the two freeze lists, `E_candidates.md`, `C_expansion_sample.json` (the random draw), `regrade_v0_with_v1_rule/` (grader self-check on v0's flights), `TASK_TEMPLATE.md` and `Dockerfile` of the whiteboard sandbox, `wb_audit.py`, `figures_v1.py` |
| `e2e/` | `E_TIMELINE.log`; `grades/` the frozen grader's file for every graded arm (`grades_excluded/`: the two whiteboard Fable arms not counted); `harness_<material>_<haiku\|fable>/` the pipeline's report, job ledger, cost, gate files, figures and the graded kernel file; `whiteboard_<material>_<haiku\|fable>/` the task sheet, notes, report, `RESULT.json`, job log, inputs, scripts and graded kernel file; `whiteboard_InPS4_mp20790_fable_invalid/` the invalid run |
| `regrade/` | `regrade_e_public.py` and `E_baselines.json`: re-grade any end-to-end kernel file with Python and numpy only |

## Re-grading the end-to-end task yourself

```
python3 regrade/regrade_e_public.py regrade/E_baselines.json CdS_mp672 e2e/whiteboard_CdS_mp672_haiku/kernel/Gamma_alphabeta_s.dat
```

The script re-implements the frozen grader from the kernel file format alone. On 2026-10-18, reading only the files in this folder, it
gave the same peaks and the same verdict as the private grader on all 27 graded arms (25 counted, 2 excluded); every published kernel
file has the sha256 recorded in its grade file.

## Materials and sealed baselines

Each arm got the same sealed cell (`structure.cif` in every whiteboard folder). An arm gives the same answer when its highest peak lies
within 0.15 eV of one of the baseline's two highest peaks, its height within 25 % of that peak and its strongest mode within 5 %.

| Material | Baseline mesh | Highest peak (eV, Å²/eV, mode THz) | Second peak |
|---|---|---|---|
| GaP (`GaP_t1`) | 96³ | 2.82, 16.0, T2 10.77 | 3.21, 10.2 |
| SnS2 (mp-1170) | 64³ | 5.46, 47.1, A1g 9.35 | 3.78, 43.2 |
| NbFeSb (mp-9437) | 64³ | 3.36, 21.3, T2 8.25 | none |
| CdS (mp-672) | 64³ | 5.79, 8.33, E2 1.15 | 4.35, 5.70 |
| KNbO3 (mp-7375) | 48³ | 3.63, 50.7, A1 7.12 | 3.96, 45.6 |
| MoS2 monolayer | 64×64×1 | 2.82, 58.7, A′1 11.89 | 5.55, 50.4 |
| InPS4 (mp-20790) | 32³ | 3.06, 67.7, A 7.87 | 4.92, 54.1 |
| Bi2O2Se | 64³ | 3.81, 28.5, A1g 4.66 | 2.37, 23.2 |

## Not published

As for v0: the harness's prompts and ticket texts, the frozen labels of the ticket and selection tasks, the pipeline code
(kernel_pipeline), raw model answers, the whiteboard sessions' full transcripts (they quote the authors' unpublished implementation
note), the bulk raw outputs of the calculations (wavefunctions, wannier90 and EPW data; the few small output logs some
whiteboard arms kept among their inputs are included). Appendix B of the report describes the private working directory these files come from;
paths, cluster project ids and user names are scrubbed from the published text.
