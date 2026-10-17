# atomost-bench v0 — the first benchmark of atomost, our agent-governance layer (2026-10-17)

**What atomost is.** A four-person team runs ten projects on one workstation with Claude agent sessions (about ten interactive
sessions a day, models from Anthropic, DeepSeek and OpenAI). atomost is the layer every session starts through. It:
- attaches the session to its project's single memory home, records and cost ledger;
- keeps one resident "strategist" session per project that curates that memory;
- provides a phone/browser console that flags sessions needing a human;
- runs daily machine check-ups.

This benchmark measures that layer, not any research pipeline.

**Rules.** Items and answer keys were frozen before any run (checksum list `design/FREEZE.sha256`). Grading is mechanical,
with no model judges. Every cell was run 3 times. Tasks 2 and 3 replay recorded history and call no model. The benchmark
measures and does not modify; defects it found are listed in the report (§8).

## Task 1 — does a fresh session follow the team's standing rules?

**Setup.**
- The same model is started headless in the project's own folder. Only the memory folder that Claude Code injects is changed:
  - **none**;
  - **native**: what Claude Code's own routing gave that project's sessions before atomost took over;
  - **atomost**: the project's curated home.
- The session may search the project folder; reads outside it were refused (audit: 56 of 58 attempts refused, the 2 others
  in one run with no effect on its graded answer).
- 43 situational multiple-choice items, each built from a rule the owner set before a fixed date, with a verbatim source quote.
- Claude Haiku 5.5 and Claude Opus 5.5; 774 runs; $57 at list price.

| 43 items × 3 runs | none | native (before atomost) | atomost home |
|---|---|---|---|
| Haiku 5.5, correct | 76.0% | 96.9% | 93.0% |
| Haiku 5.5, tokens per answer (mean) | 62.1k | 55.4k | **39.9k** |
| Haiku 5.5, seconds per answer (mean) | 10.9 | 7.9 | **7.1** |
| Opus 5.5, correct | 96.9% | 100% | 99.2% |
| Opus 5.5, tokens per answer (mean) | 51.5k | 50.8k | **37.7k** |
| Opus 5.5, USD per answer (mean, list) | 0.138 | 0.167 | **0.125** |
| Fake-premise items answered "not in the record, ask a human" | 100% | 100% | 100% |

**deeph**, where the native memory was a ledger mixing every project's rules (12 items, Opus 5.5):

| | none | mixed ledger | atomost |
|---|---|---|---|
| Correct | 100% | 100% | 100% |
| Tokens per answer | 37.1k | 64.7k | **24.6k** |
| USD per answer | 0.110 | 0.174 | **0.080** |

**Reading.**
- Project memory lifts the cheap model from 76% to 93–97% and removes most of its give-ups.
- The curated atomost home answers with 26–28% fewer tokens than the uncurated native memory.
- A mixed memory costs more than no memory at all.
- atomost does **not** make answers more accurate:
  - the strong model scores 97% with no memory, by searching the project files;
  - the cheap model scores 93% on the atomost home against 97% on the native memory.
- The cheap model's misses on the atomost home have two named causes:
  - a rule merged into the body of an overview file whose index line no longer named it;
  - a rule lost when one project's memory was moved out of the shared ledger.

## Task 2 — strategist wake policies (replay)

- A model-free script checks every project hourly and wakes its strategist only on significant change, at most once a day.
- Over 10 days that meant 435 checks and 14 automatic wakes, costing $49.
- Replaying the same checks under other policies (simulated):

| Policy | Rounds | Cost |
|---|---|---|
| A full round every hour | 435 | about $996 |
| A round at every hour with significant change | 303 | about $694 |
| An always-on session looking once an hour | 435 | about $589 |
| One fixed round a day | 23 | about $53 |

- The price of event-driven waking is waiting: a change was handled after 9.2 hours (median). The longest waits came from
  two defects:
  - a strategist that could not be woken for 3 days;
  - a failed wake that used up the day's single slot.

## Task 3 — incident replay (replay of a detection rule on history, not an observed speed-up)

- Since 09-17 there were 27 failure streaks with 55 failed replies.
- The console's rule flags each streak at its first failed record. In interactive sessions a human acted a median of
  33 minutes later.
- One loop burned 512k output tokens (about $11) on 8 replies cut at the output limit.
- After alerts went live, two unattended strategists still sat blocked for 11 and 24 hours.

## Whole-machine counts (not an experiment)

- Before atomost (09-17 to 10-05), 0 of 68 sessions loaded their own project's memory, and 53% loaded the mixed ledger.
  Since every project got a home (10-14), 15 of 15 sessions launched through atomost loaded it.
- 86% of 937 memory-maintenance actions were done by the strategist sessions; humans approve.

## Not shown

- The items are on the easy side.
- The native arm is the state frozen at takeover, not a perfect counterfactual.
- Each item is a single decision, not a full task.
- Samples are small.

## In this folder / held privately

**Published:** the report (Chinese, `report/REPORT.md`), figures, grading tables (per-answer letters and keys, no item text),
design and freeze notes, the run and figure scripts.

**Held privately (available for diligence on request):**
- the item texts and source quotes (the team's internal rules);
- the frozen memory copies;
- the per-run answers and full transcripts;
- the replay data and the atomost code.
