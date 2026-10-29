# atomost-bench v1 (2026-10-27)

The second benchmark of **atomost**, the layer every agent session of our team starts through. It measures atomost's second
round of work: rules checked by a hook at the moment a session acts, and memories delivered when the session touches what they
are about, instead of one long resident index. 30 task items in three projects, three arms (full index / lean index / lean
index + rules + injection), Haiku 5.5 and Opus 5.5, 540 runs.

- English summary: [report/SUMMARY.en.md](report/SUMMARY.en.md)
- Full report (Chinese, public edition): [report/REPORT.md](report/REPORT.md); defects handed back: [report/FINDINGS.md](report/FINDINGS.md)
- Grading tables: [tables/](tables/) (`T_runs.json` has one row per run: item id, arm, model, outcome, tokens, cost, counts; no item text)
- Design, freeze note, runner, grader, fence and hook shim: [design/](design/); `FREEZE.public.txt` holds the frozen list's checksum

The follow-up after the fixes is [atomost-bench v2](../atomost-bench-v2/).

Held privately, available for diligence on request: the item texts and fixtures (the team's internal rules), the frozen memory
copies and the frozen-file list, per-run calls, answers and transcripts, the build script and the atomost code.
