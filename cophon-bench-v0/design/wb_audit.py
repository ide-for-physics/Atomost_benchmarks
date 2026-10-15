#!/usr/bin/env python3
"""Isolation audit of the whiteboard transcripts: every tool call whose input names a forbidden tree is a hit."""
import json, re, sys, datetime
PAT = re.compile(r"9\.coherent_phonon/(kernel_pipeline|materials|_archive|theory_cache|benchmarks|whitepaper_web|phsc|epw)|exp_round1_v1|bench_b_v0|runs/GaP_e2e|runs/SnS2_e2e|runs/NbFeSb_e2e|/_library|OPERATOR_CARD|RULES\.md|casebook|wannier_events|9\.coherent_phonon/records|2\.wan_agentic_workflow|wannier_finale_root|wan_campaign|4\.memory_control|3\.insights4all")
for M in ("GaP", "SnS2", "NbFeSb"):
    f = f"<whiteboard>/{M}_whiteboard/transcript.jsonl"
    n = calls = hits = turns = 0; cost = None; last = ""
    try:
        for line in open(f):
            n += 1
            try: o = json.loads(line)
            except Exception: continue
            if o.get("type") == "result":
                turns += o.get("num_turns", 0); mu = o.get("modelUsage", {}); cost = sum(v.get("costUSD", 0) for v in mu.values()) or cost
            if o.get("type") == "assistant":
                for c in o.get("message", {}).get("content", []):
                    if c.get("type") == "tool_use":
                        calls += 1; s = json.dumps(c.get("input"))
                        if PAT.search(s): hits += 1; last = s[:160]
    except FileNotFoundError:
        continue
    print(f"{datetime.datetime.now().isoformat(timespec='seconds')} {M}: lines {n} turns {turns} calls {calls} cost {cost if cost is None else round(cost, 2)} hits {hits}" + (f" WB_AUDIT_HIT {last}" if hits else ""))
