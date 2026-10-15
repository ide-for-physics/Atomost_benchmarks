# Pillar B — Wannier projection block (first round, 16 materials; gate: score <= 0.9 and spreads <= 10 A^2)

harness-code (recipe strategy v1.1, no model, recorded 2026-10-12): 13/16 pass at round 1; with model iteration by card (recorded): 16/16 by round 3.
historical ladder (sp3 heuristics, recorded): 2/16 pass at round 1.

| arm | model | answers (material x rep) | parsable | run | pass | pass rate of run |
|---|---|---:|---:|---:|---:|---:|
| harnessmodel_r2 | deepseek-v4-flash | 9 | 8 | 7 | 0 | 0.00 |
| harnessmodel_r2 | fable | 9 | 9 | 6 | 1 | 0.17 |
| harnessmodel_r2 | haiku | 9 | 9 | 6 | 2 | 0.33 |
| harnessmodel_r2 | opus | 9 | 9 | 7 | 0 | 0.00 |
| harnessmodel_r2 | sonnet | 9 | 9 | 9 | 4 | 0.44 |
| whiteboard_r1 | deepseek-v4-flash | 48 | 20 | 19 | 4 | 0.21 |
| whiteboard_r1 | fable | 48 | 48 | 47 | 21 | 0.45 |
| whiteboard_r1 | haiku | 48 | 47 | 47 | 6 | 0.13 |
| whiteboard_r1 | opus | 48 | 48 | 48 | 19 | 0.40 |
| whiteboard_r1 | sonnet | 48 | 48 | 48 | 14 | 0.29 |
