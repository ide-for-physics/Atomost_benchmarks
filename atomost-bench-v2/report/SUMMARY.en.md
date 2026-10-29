# atomost-bench v2 — the v1 defects fixed, measured again (2026-10-27)

**The question.** [atomost-bench v1](../../atomost-bench-v1/) handed back seven defects in atomost's rules and memory injection.
They were fixed in atomost v1.71–v1.74, together with three rules the owner moved to a new level, *block once* (the first
attempt is refused with the reason; the same attempt repeated goes through), and with narrower triggers for the memories
that had been sent off-topic. Did the items that exposed the defects actually improve? Do the success criteria still hold
(resident context smaller, tokens not up, rule-keeping not down)?

## Setup

- v1's 30 items, unchanged (every file's checksum identical to v1), its grader, fence and run procedure.
- Arms **F** (full index, no hooks) and **N** (lean index + rules + injection). L was not rerun: v1 had already shown that
  trimming the index alone loses rules. F was rerun on the same day so both arms use the same memory snapshot.
- Frozen 581 files (atomost's code and rules as committed in 4f7ffbb), 0 changed after the runs.
- 30 × 2 arms × 2 models × 3 runs = **360 runs**, 54 minutes, **$26.81 at list price** (Haiku $0.99, Opus $25.82).
  0 errors, 0 benchmark rows in the real ledgers.

## Results

**Every fix works mechanically. The success criteria still hold, but the gain in rule-keeping is about the same as in v1, not larger.**

| | Haiku F | Haiku N | Opus F | Opus N |
|---|---|---|---|---|
| Resident context at start (median, tokens) | 13,977 | 12,275 (−12%) | 13,146 | 11,446 (−13%) |
| Tokens per run (mean) | 115,608 | 116,507 (+1%) | 88,239 | 91,991 (+4%) |
| Rule kept, frozen answer key | 67/89 | 75/90 | 81/90 | 85/89 |
| Rule kept, a blocked attempt not counted as broken | 67/89 | 80/90 | 81/90 | 88/89 |
| Task done (of 90) | 88 | 85 | 83 | 85 |

- **Tokens**: paired by item, N costs 2–3% more than F for both models, p≈0.6: no measurable difference. Opus's extra is
  in the machine-wide rule items, where *block once* adds a step.
- **Rule-keeping**: by the frozen key N keeps 8 (Haiku) and 4 (Opus) more runs; p≈0.19 and 0.50. The unchanged F arm moved
  from 75 to 81 for Opus between v1 and v2. **Same conditions, two days apart, 6 runs of difference**, so totals within ±5
  are noise. The per-item mechanisms are what counts.
- **A flaw of the benchmark's own answer key**: two items' keys were written for v1, when the rule only reminded after the
  fact, and count the blocked attempt itself as a violation. Now the rule blocks first; the session is stopped, corrects
  itself and redoes it, which the authoring rules call kept. Both rows are reported; the second changes only those two items.

**Each v1 defect** (runs kept out of 3 in arm N, v1 → v2):

| v1 defect | Haiku | Opus | What happened in v2 | Fixed? |
|---|---|---|---|---|
| relative paths in the owner's message did not trigger injection | 2→1 | 3→3 | delivered in all 6 runs | delivery fixed |
| multi-line parallel-ssh loop not recognised | 3→3 | 3→3 | no session wrote such a loop | not measurable (checked on the frozen engine) |
| a reminder arrives after the action | 0→0 (3*) | 1→0 (3*) | every run: first `ssh` blocked, handbook read, `ssh` allowed | fixed |
| heavy-job rule missed env-variable prefixes | 3→2 | 2→3 | 4 blocked and redone through the box; one missed `timeout 600 mpirun` | mostly; new defect 8 |
| input-file rule missed shell writes | 1→3 | 0→3 | all 6 got the reminder and corrected the file | fixed |
| reminders did not say who set the rule | same item | | Haiku: "the hook says the owner's rule…, so I changed it" | fixed |

\* v2 with a blocked attempt not counted as broken.

**False deliveries**: 122 → 94 pointers sent, off-topic 26 (21%) → 3 (3%). Needed deliveries did not drop: 26 → 27
(Haiku) and 26 → 25 (Opus) of 27 runs.

**New defect 8**: the heavy-job rule still missed a `timeout` prefix. atomost's answer (v1.76) was not another pattern in the
rule but a guard one layer down: it watches the processes agent sessions start and moves any heavy job outside the shared
compute box into it, whatever the command was called. The rule stays as an early reminder.

## Limits

- 3 runs per cell, and the same conditions drift by 6 runs in two days; small total differences are not claims.
- The frozen key counts blocked attempts as broken on two items (reported apart). The benchmark's fence wrongly refused one
  reasonable command, and the run environment still had the real agent binary on its PATH (no run called it); both to be
  fixed in the next version.
- Injected pointers name the benchmark's folders, so a session can tell it is a test (same as v1).

## Not in this repository

As for v1: item texts and fixtures, memory copies, the frozen-file list (its checksum is published), per-run tool calls,
answers and transcripts, the build script and atomost's code are held privately and available for diligence on request.
