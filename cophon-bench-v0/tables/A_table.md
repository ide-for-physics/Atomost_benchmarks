# Pillar A — operator tickets (median over repeats)

strict = the sealed bench's score (validator legality + class; harness arm only); class = action-class score (both arms; whiteboard generic actions mapped onto the ticket's classes). Max = number of tickets.

| arm | model | tickets | repeats | strict score | class score | compute-burning answers | over-escalations | illegal / unmappable |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| harness | deepseek-v4-flash | 44 | 3 | 35.5 | 35.75 | 0 | 1 | 2 |
| harness | fable | 44 | 3 | 38.0 | 38.0 | 0 | 3 | 0 |
| harness | haiku | 44 | 3 | 34.75 | 36.25 | 0 | 6 | 1 |
| harness | opus | 44 | 3 | 38.25 | 38.25 | 0 | 3 | 0 |
| harness | sonnet | 44 | 3 | 37.5 | 38.75 | 0 | 4 | 0 |
| whiteboard | deepseek-v4-flash | 44 | 3 | - | 28.5 | 5 | 0 | 0 |
| whiteboard | fable | 44 | 3 | - | 28.5 | 5 | 0 | 0 |
| whiteboard | haiku | 44 | 3 | - | 29.0 | 4 | 7 | 0 |
| whiteboard | opus | 44 | 3 | - | 31.75 | 5 | 0 | 0 |
| whiteboard | sonnet | 44 | 3 | - | 29.0 | 7 | 2 | 0 |

Reference: escalate-everything scores 32.50 of 44 (class score) with zero burns.
