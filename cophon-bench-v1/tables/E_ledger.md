# Pillar E — status and cost of every arm (built by e_close_v1.py; verdicts from the frozen pillar_e.py)

| material | arm | status | verdict | node-h | wall h | model $ (list) | tickets | human touches | note |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| GaP_t1 | harness+Haiku | finished | same answer | 0.61 | 3.3 | 0.02 | 9 | 0 |  |
| GaP_t1 | harness+Fable | finished | same answer | 0.62 | 3.0 | 3.96 | 10 | 0 |  |
| GaP_t1 | whiteboard Haiku | finished | same answer | 0.654 | 4.8 | 1.9 | — | 0 |  |
| GaP_t1 | whiteboard Fable | finished | same answer | 5.18 | 35.47 | 30.5 | — | 0 |  |
| SnS2_mp1170 | harness+Haiku | finished | same answer | 1.19 | 5.0 | 0.02 | 1 | 0 |  |
| SnS2_mp1170 | harness+Fable | finished | same answer | 1.23 | 5.0 | 0.62 | 1 | 0 |  |
| SnS2_mp1170 | whiteboard Haiku | finished | same answer | 2.453 | 2.4 | 3.21 | — | 0 |  |
| SnS2_mp1170 | whiteboard Fable | finished | same answer | 4.841 | 29.92 | 20.89 | — | 0 |  |
| NbFeSb_mp9437 | harness+Haiku | finished | same answer | 5.8 | 7.9 | 0.01 | 4 | 0 |  |
| NbFeSb_mp9437 | harness+Fable | finished | same answer | 5.74 | 8.6 | 2.81 | 8 | 0 |  |
| NbFeSb_mp9437 | whiteboard Haiku | finished | same answer | 9.42 | 12.2 | 4.31 | — | 0 |  |
| NbFeSb_mp9437 | whiteboard Fable | finished | same answer | 4.468 | 3.7 | 19.27 | — | 0 |  |
| CdS_mp672 | harness+Haiku | finished | same answer | 4.75 | 4.1 | 0.02 | 7 | 0 |  |
| CdS_mp672 | harness+Fable | finished | same answer | 4.05 | 3.9 | 1.37 | 5 | 0 |  |
| CdS_mp672 | whiteboard Haiku | finished | differs: height | 4.26 | 6.05 | 4.84 | — | 0 |  |
| CdS_mp672 | whiteboard Fable | finished | differs: height | 9.096 | 9.53 | 30.2 | — | 0 |  |
| KNbO3_mp7375 | harness+Haiku | finished | same answer | 2.98 | 10.5 | 0.02 | 4 | 1 |  |
| KNbO3_mp7375 | harness+Fable | not finished | — | 3.66 | 26.0 | 11.15 | 7 | 2 | dropped at epw1 by the owner's drop rule (harness did not finish; line-2 handoff) |
| KNbO3_mp7375 | whiteboard Haiku | finished | differs: position, height | 1.94 | 2.1 | 2.35 | — | 0 |  |
| KNbO3_mp7375 | whiteboard Fable | finished | differs: position, height | 6.102 | 5.8 | 30.65 | — | 0 |  |
| InPS4_mp20790 | harness+Haiku | not finished | — | 2.31 | 21.0 | 0.06 | 17 | 2 | dropped at epw1 by the owner's drop rule (harness did not finish; line-2 handoff) |
| InPS4_mp20790 | harness+Fable | not finished | — | 2.28 | 26.0 | 10.41 | 16 | 2 | dropped at wannier by the owner's drop rule (harness did not finish; line-2 handoff) |
| InPS4_mp20790 | whiteboard Haiku | finished | same answer | 5.41 | 5.03 | 8.16 | — | 0 |  |
| InPS4_mp20790 | whiteboard Fable | invalid | same answer | 8.59 | 33.7 | 22.67 | — | 0 | reused the whiteboard Haiku arm's calculations (shared remote root); not rerun (LUMI closed) |
| Bi2O2Se | harness+Haiku | not finished | — | 22.98 | 19.4 | 0.01 | 1 | 1 | dropped at epw1 by the owner's drop rule (harness did not finish; line-2 handoff) |
| Bi2O2Se | harness+Fable | not finished | — | 22.62 | 24.4 | 4.96 | 3 | 1 | dropped at epw1 by the owner's drop rule (harness did not finish; line-2 handoff) |
| Bi2O2Se | whiteboard Haiku | finished | same answer | 8.83 | 12.3 | 7.52 | — | 0 |  |
| Bi2O2Se | whiteboard Fable | stopped | same answer | 4.3 | 7.5 | 66.51 | — | 0 | stopped by the bench at its provisional 64x64x64 answer (LUMI closed); not counted |
| MoS2_monolayer | harness+Haiku | finished | same answer | 0.27 | 1.5 | 0.02 | 1 | 0 |  |
| MoS2_monolayer | harness+Fable | finished | same answer | 0.28 | 1.5 | 1.52 | 1 | 0 |  |
| MoS2_monolayer | whiteboard Haiku | finished | same answer | 0.36 | 0.95 | 2.06 | — | 0 |  |
| MoS2_monolayer | whiteboard Fable | finished | same answer | 0.5119 | 1.27 | 21.18 | — | 0 |  |

## Per arm type (scored = finished arms only)

| arm | finished | same answer | differs | not finished | invalid / stopped | node-h (finished) | model $ (all) | human touches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| harness+Haiku | 6/8 | 6 | 0 | 2 | 0 | 15.6 | 0.18 | 4 |
| harness+Fable | 5/8 | 5 | 0 | 3 | 0 | 11.9 | 36.80 | 5 |
| whiteboard Haiku | 8/8 | 6 | 2 | 0 | 0 | 33.3 | 34.35 | 0 |
| whiteboard Fable | 6/8 | 4 | 2 | 0 | 2 | 30.2 | 241.87 | 0 |
