# Pillar C — batch selection of 8 from the unique-formula pool (median over repeats)

Pool: 37 materials; promising (Screening Baseline v2): 4; line-hit & radiating: 15.

| arm | model | legal answers | promising picks (of 8) | line-hit & radiating picks | sum of main score (mid) | sum of kernel peaks Å²/eV |
|---|---|---:|---:|---:|---:|---:|
| random 8 (expectation) | - | - | 0.86 | 3.24 | 5.187 | - |
| harness-code (top-8 prior score) | - | - | 0 | 5 | 4.241 | 162.4 |
| oracle (top-8 by main score) | - | - | 4 | 6 | 18.584 | 415.2 |
| whiteboard | fable | 3/3 | 3 | 4 | 12.761 | 485.7 |
| whiteboard | haiku | 3/3 | 2 | 2 | 9.426 | 212.9 |
| whiteboard | opus | 3/3 | 4 | 5 | 15.416 | 585.9 |
| whiteboard | sonnet | 3/3 | 2 | 4 | 10.35 | 293.0 |
| harness | fable | 3/3 | 3 | 6 | 13.756 | 382.8 |
| harness | haiku | 3/3 | 1 | 5 | 6.984 | 190.8 |
| harness | opus | 3/3 | 3 | 5 | 13.634 | 371.4 |
| harness | sonnet | 3/3 | 2 | 4 | 11.466 | 215.9 |

## Loop-discovered pool only (23 materials; picks outside it are dropped before counting)

promising in this pool: 1; line-hit & radiating: 9.

| arm | model | picks inside the pool (median) | promising | line-hit & radiating | sum of main score (mid) | sum of kernel peaks |
|---|---|---:|---:|---:|---:|---:|
| random 8 (expectation, pool only) | - | 8 | 0.35 | 3.13 | 3.501 | - |
| harness-code (top-8 prior score) | - | 8 | 0 | 5 | 4.241 | 162.4 |
| oracle (top-8 by main score, pool) | - | 8 | 1 | 7 | 8.53 | 342.4 |
| whiteboard | fable | 3 | 0 | 2 | 0.609 | 100.8 |
| whiteboard | haiku | 3 | 0 | 0 | 0.21 | 31.7 |
| whiteboard | opus | 3 | 1 | 2 | 3.688 | 162.8 |
| whiteboard | sonnet | 4 | 0 | 1 | 0.889 | 135.4 |
| harness | fable | 6 | 1 | 5 | 6.816 | 273.9 |
| harness | haiku | 7 | 0 | 4 | 3.657 | 134.1 |
| harness | opus | 6 | 1 | 4 | 5.613 | 264.0 |
| harness | sonnet | 6 | 0 | 3 | 3.566 | 115.2 |
