# Pillar C — batch selection of 8 from the unique-formula pool (median over repeats)

Pool: 47 materials; promising (Screening Baseline v2): 4; line-hit & radiating: 16.

| arm | model | legal answers | promising picks (of 8) | line-hit & radiating picks | sum of main score (mid) | sum of kernel peaks Å²/eV |
|---|---|---:|---:|---:|---:|---:|
| random 8 (expectation) | - | - | 0.68 | 2.72 | 4.213 | - |
| harness-code (top-8 prior score) | - | - | 0 | 5 | 4.241 | 162.4 |
| oracle (top-8 by main score) | - | - | 4 | 6 | 18.584 | 415.2 |
| whiteboard | deepseek-v4-flash | 3/5 | 3 | 2 | 11.843 | 214.6 |
| whiteboard | fable | 5/5 | 3 | 3 | 12.875 | 505.3 |
| whiteboard | haiku | 5/5 | 3 | 2 | 11.686 | 220.2 |
| whiteboard | opus | 5/5 | 3 | 3 | 12.704 | 503.4 |
| whiteboard | sonnet | 4/5 | 2 | 3 | 9.764 | 230.8 |
| harness | deepseek-v4-flash | 5/5 | 1 | 5 | 6.932 | 206.7 |
| harness | fable | 5/5 | 3 | 5 | 14.315 | 356.0 |
| harness | haiku | 5/5 | 2 | 5 | 11.212 | 243.0 |
| harness | opus | 5/5 | 3 | 5 | 13.71 | 339.2 |
| harness | sonnet | 4/5 | 1 | 4 | 8.749 | 198.2 |

## Loop-discovered pool only (33 materials; picks outside it are dropped before counting)

promising in this pool: 1; line-hit & radiating: 10.

| arm | model | picks inside the pool (median) | promising | line-hit & radiating | sum of main score (mid) | sum of kernel peaks |
|---|---|---:|---:|---:|---:|---:|
| random 8 (expectation, pool only) | - | 8 | 0.24 | 2.42 | 2.625 | - |
| harness-code (top-8 prior score) | - | 8 | 0 | 5 | 4.241 | 162.4 |
| oracle (top-8 by main score, pool) | - | 8 | 1 | 6 | 8.601 | 361.9 |
| whiteboard | deepseek-v4-flash | 2 | 0 | 0 | 0.179 | 22.6 |
| whiteboard | fable | 3 | 0 | 0 | 0.72 | 66.9 |
| whiteboard | haiku | 3 | 0 | 0 | 0.648 | 63.3 |
| whiteboard | opus | 3 | 0 | 0 | 0.72 | 66.9 |
| whiteboard | sonnet | 4 | 0 | 1 | 1.189 | 91.8 |
| harness | deepseek-v4-flash | 6 | 0 | 4 | 3.172 | 134.1 |
| harness | fable | 6 | 1 | 4 | 6.275 | 247.1 |
| harness | haiku | 6 | 0 | 4 | 3.172 | 134.1 |
| harness | opus | 6 | 1 | 4 | 5.67 | 230.3 |
| harness | sonnet | 6 | 0 | 4 | 3.192 | 134.1 |
