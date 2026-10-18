# cophon-bench v1 — cost (built by costs_v1.py)

## Model spend, list price (USD)

| item | by model | total |
|---|---|---:|
| A (main reps 4-5, hold-out reps 1-5) | deepseek-v4-flash 0.52 (246 calls), fable 206.14 (246 calls), haiku 1.44 (246 calls), opus 63.78 (246 calls), sonnet 26.41 (246 calls) | 298.29 |
| B round 3 answers | deepseek-v4-flash 0.27 (29 calls), fable 39.00 (21 calls), haiku 0.25 (38 calls), opus 10.31 (22 calls), sonnet 2.96 (27 calls) | 52.79 |
| C stage 2 answers | deepseek-v4-flash 0.08 (10 calls), fable 20.42 (10 calls), haiku 0.61 (10 calls), opus 5.91 (10 calls), sonnet 2.82 (10 calls) | 29.85 |
| E ticket relay (harness arms) | fable 36.80, haiku 0.18 | 36.98 |
| C expansion ticket relay | haiku 0.25 (28 calls) | 0.25 |
| E whiteboard arms | fable 241.87, haiku 34.35 | 276.22 |
| E whiteboard attempts cut by a limit before working | fable/haiku 0.00 | 0.00 |
| **total** | deepseek-v4-flash 0.87, fable 544.23, haiku 37.08, opus 80.00, sonnet 32.19 | **694.38** |

## Cluster node-hours

| item | node-hours |
|---|---:|
| E harness arms (16) | 81.4 |
| E harness first attempts (_attempt1, 6) | 0.1 |
| E whiteboard arms (16, self-reported) | 76.4 |
| C expansion (10 materials) | 46.9 |
| A, B round 3, C answers | 0.0 |
| **total** | **204.8** |
