#!/usr/bin/env python3
"""atomost-bench v0, task 1: does a fresh agent session follow the team's standing rules?

The same model, started headless in the project's own folder, gets one of three memory folders injected by Claude Code
(--settings autoMemoryDirectory): none (empty), native (what Claude Code's own routing gave that project's sessions before
atomost took over, frozen copy), atomost (the project's curated memory home, frozen copy). It may search the project folder
with Read/Grep/Glob; reads outside the project folder and the memory folder are refused (headless runs cannot grant
permission; smoke-tested 2026-10-17). User settings, hooks and MCP servers are off (--setting-sources project,local
--strict-mcp-config); the global ~/.claude/CLAUDE.md is still loaded in every arm (smoke-tested), so it is a constant.

    python3 t1_bench.py prompts                                  # items/items.json -> prompts/<id>.prompt.txt
    python3 t1_bench.py run --arms none,native,atomost --models haiku,opus --reps 3 [--jobs 3] [--only C01,D02]
    python3 t1_bench.py grade                                    # results/ -> tables/T1.md, tables/t1_detail.json

Grading is mechanical: the chosen letter against the frozen key. No model judges. Runs never write the project folder
(write tools are not offered) and each run gets a fresh temporary copy of its memory folder.
"""
from __future__ import annotations
import argparse, json, os, re, shutil, statistics as st, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = HERE.parent / "atomost-bench-v0"
ITEMS = Path(os.environ.get("AB_ITEMS", str(V / "items" / "items.json")))
RESULTS = Path(os.environ.get("AB_RESULTS", str(V / "results")))
PROMPTS = Path(os.environ.get("AB_PROMPTS", str(V / "prompts")))
ROOTS = {"cophon": "~/9.coherent_phonon", "deeph": "~/11.deeph", "new-tech-tests": "~/7.new_tech_tests"}
MODELS = {"haiku": "claude-haiku-5-5", "opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5"}
ARMS = ("none", "native", "atomost")
MAX_TURNS = "10"
SCRATCH = Path(tempfile.gettempdir()) / "atomost-bench-v0-runs"
LIMIT_TEXTS = ("hit your session limit", "hit your usage limit", "usage limit reached", "rate limit", "rate_limit", "overloaded",
               "you've reached your", "hit your weekly limit")

PROMPT = """你是刚在这个项目文件夹里启动的一个新会话（Claude Code）。同事交给你下面这件事，你要先决定怎么做。
请按这个项目已经定下的规矩、决定和偏好来选。需要的话可以用 Read / Grep / Glob 查项目文件夹里的文件，但别做与本题无关的事。
如果这个项目确实没有相关的规矩或决定，就选 E。

情况：{question}

{options}

最后只输出一行 JSON，不要别的文字：{{"choice": "A、B、C、D、E 之一", "source": "依据：记忆 / 某个文件路径 / 常识", "why": "一句话"}}
"""


def load_items() -> list[dict]:
    return json.loads(ITEMS.read_text())


def cmd_prompts(a) -> int:
    out = PROMPTS
    out.mkdir(parents=True, exist_ok=True)
    for it in load_items():
        opts = "\n".join(f"{k}. {it['options'][k]}" for k in "ABCDE")
        (out / f"{it['id']}.prompt.txt").write_text(PROMPT.format(question=it["question"], options=opts))
    print(f"{len(load_items())} prompts in {out}")
    return 0


def parse_answer(text: str) -> dict | None:
    s = (text or "").strip()
    for m in re.finditer(r"\{[^{}]*\}", s, re.S):
        try:
            d = json.loads(m.group(0))
            if isinstance(d, dict) and "choice" in d:
                c = str(d.get("choice", "")).strip().upper()[:1]
                d["choice"] = c if c in "ABCDE" and c else None
                return d
        except json.JSONDecodeError:
            continue
    m = re.search(r'"choice"\s*:\s*"([A-E])', s)
    return {"choice": m.group(1)} if m else None


def parse_stream(lines: list[str]) -> dict:
    """final text, result event, tool calls, refused calls, paths touched, context size of the first API call."""
    out = {"final": "", "result": {}, "calls": 0, "refused": 0, "paths": [], "ctx0": None}
    for ln in lines:
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            out["result"] = ev
            out["final"] = ev.get("result") or out["final"]
        msg = ev.get("message")
        if not isinstance(msg, dict):
            continue
        u = msg.get("usage")
        if ev.get("type") == "assistant" and isinstance(u, dict) and out["ctx0"] is None:
            out["ctx0"] = (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
        for b in msg.get("content") if isinstance(msg.get("content"), list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                out["calls"] += 1
                inp = b.get("input") or {}
                for k in ("file_path", "path", "pattern"):
                    if inp.get(k):
                        out["paths"].append(f"{b.get('name')}:{inp[k]}")
            if b.get("type") == "tool_result" and b.get("is_error") and re.search(r"permission|not allowed|denied|blocked", str(b.get("content")), re.I):
                out["refused"] += 1
    return out


def run_one(item: dict, arm: str, model: str, out: Path, timeout: int) -> dict:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    mem = Path(tempfile.mkdtemp(prefix=f"{arm}_{item['id']}_", dir=SCRATCH))
    src = V / "arms" / item["project"] / arm
    for f in src.glob("*.md"):
        shutil.copy2(f, mem / f.name)
    cmd = ["claude", "-p", "--model", MODELS[model], "--output-format", "stream-json", "--verbose", "--no-session-persistence",
           "--setting-sources", "project,local", "--strict-mcp-config", "--max-turns", MAX_TURNS, "--tools", "Read,Grep,Glob",
           "--settings", json.dumps({"autoMemoryDirectory": str(mem)})]
    prompt = (PROMPTS / f"{item['id']}.prompt.txt").read_text()
    t0 = time.time()
    try:
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ROOTS[item["project"]], timeout=timeout)
        lines = p.stdout.splitlines()
        s = parse_stream(lines)
        u = s["result"].get("usage") or {}
        usage = {"model": model, "arm": arm, "usd": s["result"].get("total_cost_usd"), "seconds": round(time.time() - t0, 1),
                 "turns": s["result"].get("num_turns"), "stop": s["result"].get("subtype"), "tool_calls": s["calls"],
                 "refused_calls": s["refused"], "ctx0": s["ctx0"], "input": u.get("input_tokens"),
                 "cache_read": u.get("cache_read_input_tokens"), "cache_write": u.get("cache_creation_input_tokens"),
                 "output": u.get("output_tokens"), "stderr": p.stderr[-300:] if p.returncode else ""}
        final, paths = s["final"], s["paths"]
    except subprocess.TimeoutExpired:
        lines, final, paths = [], "", []
        usage = {"model": model, "arm": arm, "error": f"timeout {timeout}s", "seconds": timeout}
    finally:
        shutil.rmtree(mem, ignore_errors=True)
    rec = {"item": item["id"], "answer": parse_answer(final), "raw": final[-2000:], "paths": paths[:60], "usage": usage}
    if any(t in (final or "").lower() for t in LIMIT_TEXTS) and len(final or "") < 600:
        rec["usage"]["error"] = "session limit"
        print(f"SESSION LIMIT {arm} {model} {item['id']}: {final[:80]!r}", flush=True)
        return rec
    out.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    out.with_suffix(".transcript.jsonl").write_text("\n".join(lines) + "\n")
    return rec


def run_paced(item, arm, model, out, a, stop_file) -> dict:
    rec = {"usage": {"error": "not run"}}
    for _ in range(a.limit_retries + 1):
        if stop_file.is_file():
            return {"usage": {"error": "stopped"}}
        if a.pace:
            time.sleep(a.pace)
        rec = run_one(item, arm, model, out, a.timeout)
        if rec["usage"].get("error") != "session limit":
            return rec
        waited = 0.0
        while waited < a.limit_wait * 60 and not stop_file.is_file():
            time.sleep(30)
            waited += 30
    return rec


def cmd_run(a) -> int:
    items = load_items()
    if a.only:
        want = set(a.only.split(","))
        items = [i for i in items if i["id"] in want]
    root = RESULTS
    stop_file = root / "STOP"
    tasks = []
    for rep in range(1, a.reps + 1):              # rep-major order: a stop part-way leaves whole reps, not whole arms
        for model in a.models.split(","):
            for arm in a.arms.split(","):
                for it in items:
                    out = root / arm / model / f"rep{rep}" / f"{it['id']}.json"
                    if out.is_file():
                        continue
                    out.parent.mkdir(parents=True, exist_ok=True)
                    tasks.append((it, arm, model, rep, out))
    print(f"{len(tasks)} runs to do", flush=True)
    usd, done = 0.0, 0
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(run_paced, it, arm, m, out, a, stop_file): (it["id"], arm, m, rep) for it, arm, m, rep, out in tasks}
        for f in as_completed(futs):
            iid, arm, m, rep = futs[f]
            u = f.result().get("usage", {})
            usd += u.get("usd") or 0
            done += 1
            print(f"[{done}/{len(tasks)}] {arm} {m} rep{rep} {iid}: ${u.get('usd') or 0:.3f} {u.get('turns')} turns "
                  f"{u.get('tool_calls')} calls ctx0 {u.get('ctx0')} {u.get('seconds')}s {u.get('error', '')} (total ${usd:.2f})", flush=True)
    return 0


def cmd_grade(a) -> int:
    items = {i["id"]: i for i in load_items()}
    rows = []
    for f in sorted(RESULTS.glob("*/*/rep*/*.json")):
        arm, model, rep = f.parts[-4], f.parts[-3], f.parts[-2]
        r = json.loads(f.read_text())
        it = items.get(r["item"])
        if not it:
            continue
        ch = (r.get("answer") or {}).get("choice")
        u = r.get("usage") or {}
        tok = sum((u.get(k) or 0) for k in ("input", "cache_read", "cache_write", "output"))
        rows.append({"item": it["id"], "project": it["project"], "kind": it["kind"], "arm": arm, "model": model, "rep": rep,
                     "choice": ch, "key": it["key"], "correct": ch == it["key"],
                     "trap_hit": bool(it.get("trap_option")) and ch == it.get("trap_option"),
                     "asked_human": ch == "E" and it["kind"] != "fake", "no_answer": ch is None,
                     "usd": u.get("usd") or 0, "tokens": tok, "ctx0": u.get("ctx0"), "seconds": u.get("seconds"),
                     "tool_calls": u.get("tool_calls") or 0, "refused": u.get("refused_calls") or 0, "error": u.get("error")})
    (V / "tables").mkdir(parents=True, exist_ok=True)
    (V / "tables" / "t1_detail.json").write_text(json.dumps(rows, indent=0, ensure_ascii=False))

    def cell(sel):
        if not sel:
            return None
        reps = sorted({r["rep"] for r in sel})
        per_rep = [sum(r["correct"] for r in sel if r["rep"] == k) for k in reps]
        return {"n_items": len({r["item"] for r in sel}), "reps": len(reps), "correct_mean": st.mean(per_rep),
                "acc": sum(r["correct"] for r in sel) / len(sel), "trap": sum(r["trap_hit"] for r in sel),
                "asked": sum(r["asked_human"] for r in sel), "none": sum(r["no_answer"] for r in sel),
                "usd_med": st.median(r["usd"] for r in sel), "tok_med": st.median(r["tokens"] for r in sel),
                "ctx0_med": st.median([r["ctx0"] for r in sel if r["ctx0"]] or [0]), "sec_med": st.median((r["seconds"] or 0) for r in sel),
                "calls_med": st.median(r["tool_calls"] for r in sel), "refused": sum(r["refused"] for r in sel)}

    out = ["# atomost-bench v0 · task 1 tables (generated by t1_bench.py grade)", ""]
    groups = [("all projects", lambda r: True)] + [(p, (lambda p: lambda r: r["project"] == p)(p)) for p in ROOTS]
    for title, flt in groups:
        out += [f"## {title}", "", "| model | arm | items | correct (mean over reps) | accuracy | trap hits | asked human (non-fake) | no answer | "
                "median $ / run | median tokens / run | median context at start | median s | median tool calls | refused reads |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for m in sorted({r["model"] for r in rows}):
            for arm in ARMS:
                c = cell([r for r in rows if flt(r) and r["model"] == m and r["arm"] == arm])
                if c:
                    out.append(f"| {m} | {arm} | {c['n_items']} | {c['correct_mean']:.1f} | {c['acc']:.0%} | {c['trap']} | {c['asked']} | {c['none']} | "
                               f"{c['usd_med']:.3f} | {c['tok_med']:,.0f} | {c['ctx0_med']:,.0f} | {c['sec_med']:.0f} | {c['calls_med']:.0f} | {c['refused']} |")
        out.append("")
    out += ["## by kind (all projects)", "", "| model | kind | " + " | ".join(ARMS) + " |", "|---|---|" + "---|" * len(ARMS)]
    for m in sorted({r["model"] for r in rows}):
        for kind in sorted({r["kind"] for r in rows}):
            vals = []
            for arm in ARMS:
                c = cell([r for r in rows if r["model"] == m and r["kind"] == kind and r["arm"] == arm])
                vals.append(f"{c['acc']:.0%} (n={c['n_items']})" if c else "-")
            out.append(f"| {m} | {kind} | " + " | ".join(vals) + " |")
    (V / "tables" / "T1.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prompts")
    r = sub.add_parser("run")
    r.add_argument("--arms", default="none,native,atomost")
    r.add_argument("--models", default="haiku")
    r.add_argument("--reps", type=int, default=3)
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--only", default="")
    r.add_argument("--timeout", type=int, default=420)
    r.add_argument("--pace", type=float, default=2.0)
    r.add_argument("--limit-wait", type=float, default=20.0, help="minutes to wait after a subscription-limit reply")
    r.add_argument("--limit-retries", type=int, default=12)
    sub.add_parser("grade")
    a = ap.parse_args()
    return {"prompts": cmd_prompts, "run": cmd_run, "grade": cmd_grade}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
