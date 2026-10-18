# Pillar A — operator tickets (median over repeats)

strict = the sealed bench's score (validator legality + class; harness arm only); class = action-class score (both arms; whiteboard generic actions mapped onto the ticket's classes). Max = number of tickets.

| set | arm | model | tickets | repeats | strict score | class score | compute-burning answers | over-escalations | illegal / unmappable |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| main | harness | deepseek-v4-flash | 44 | 5 | 34.75 | 35.75 | 0 | 1 | 2 |
| main | harness | fable | 44 | 5 | 38.0 | 38.0 | 0 | 3 | 0 |
| main | harness | haiku | 44 | 5 | 34.25 | 35.75 | 0 | 6 | 1 |
| main | harness | opus | 44 | 5 | 38.25 | 38.25 | 0 | 3 | 0 |
| main | harness | sonnet | 44 | 5 | 37.75 | 38.25 | 0 | 4 | 0 |
| main | whiteboard | deepseek-v4-flash | 44 | 5 | - | 27.25 | 6 | 0 | 0 |
| main | whiteboard | fable | 44 | 5 | - | 28.25 | 5 | 0 | 0 |
| main | whiteboard | haiku | 44 | 5 | - | 29.0 | 4 | 6 | 0 |
| main | whiteboard | opus | 44 | 5 | - | 31.75 | 4 | 0 | 0 |
| main | whiteboard | sonnet | 44 | 5 | - | 28.5 | 7 | 2 | 0 |
| holdout | harness | deepseek-v4-flash | 7 | 5 | 5.5 | 5.5 | 1 | 0 | 0 |
| holdout | harness | fable | 7 | 5 | 7.0 | 7.0 | 0 | 0 | 0 |
| holdout | harness | haiku | 7 | 5 | 6.5 | 6.5 | 0 | 0 | 0 |
| holdout | harness | opus | 7 | 5 | 7.0 | 7.0 | 0 | 0 | 0 |
| holdout | harness | sonnet | 7 | 5 | 6.5 | 6.5 | 0 | 0 | 0 |
| holdout | whiteboard | deepseek-v4-flash | 7 | 5 | - | 3.75 | 1 | 0 | 1 |
| holdout | whiteboard | fable | 7 | 5 | - | 5.5 | 0 | 1 | 0 |
| holdout | whiteboard | haiku | 7 | 5 | - | 4.75 | 1 | 0 | 0 |
| holdout | whiteboard | opus | 7 | 5 | - | 5.0 | 0 | 2 | 0 |
| holdout | whiteboard | sonnet | 7 | 5 | - | 6.0 | 0 | 0 | 0 |

Reference (main): escalate-everything scores 32.50 of 44 (class score) with zero burns.

Reference (holdout): escalate-everything scores 4.00 of 7 (class score) with zero burns.
