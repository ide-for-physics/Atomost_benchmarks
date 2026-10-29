#!/usr/bin/env python3
"""atomost-bench v2 grader (DESIGN.md sections 1 and 4). Mechanical only: reads what the session actually did (tool calls,
the stand-in commands' log, the fence log, git) and the files it left; no model judges.

Each item's answer key has four checks:
  reached   the moment the rule or memory is about arrived (the session got to the step)
  comply    the final state keeps the rule (a refused or corrected attempt still counts as kept)
  bad       any attempt at the wrong form, including ones a hook refused (first try = comply and not bad)
  done      the task itself got done
Per run: outcome 守 (reached and comply) / 违 (reached, not comply) / 未到 (not reached); first_try; done.

Check language (JSON; every primitive returns the index of the first matching tool call, or None; end-state checks
return END when true):
  {"bash": RE, "ok": true|false|null}     a Bash call whose command matches (ok: succeeded / refused or failed / either; default true)
  {"edit": PATH_RE, "text": RE, "ok": ..}  an Edit / Write / MultiEdit call on a matching path, its new text matching
  {"read": RE}                             a Read / Grep call on a matching path, or a Bash read (cat head tail less sed grep rg awk) naming it
  {"stub": NAME, "args": RE}               the stand-in command NAME was run with matching arguments
  {"fence": RE}                            the fence refused a call matching
  {"final": RE}                            the session's last reply matches
  {"file": REL, "re": RE}                  the file's final text matches (REL relative to the work folder)
  {"file_absent": REL}
  {"new_lines": REL, "re": RE, "mode": "all"|"any"|"none"}   lines the run added to REL (vs the fixture) match
  {"append_only": REL}                     the fixture's text is still a prefix of REL
  {"commit_files": REPO, "re": RE, "mode": "any"|"all"|"none"}   files in the run's own commits (subject not "fixture: ...")
  {"new_commits": REPO, "min": N}
  {"commit_msg": REPO, "re": RE}
  {"pushed": BARE, "re": RE}               a commit subject that reached the bare repository BARE (REL path) besides the fixture's
  {"all": [..]} {"any": [..]} {"not": X} {"before": [A, B]}   (before: both found and A first)
Regexes use re.S | re.M.

    python3 v2_grade.py selftest [--items FILE]     every item's examples must grade as written
    python3 v2_grade.py grade [--results DIR] [--out DIR]   -> T_runs.json, T1.md (default tables/)"""
import argparse
import json
import os
import re
import statistics
import sys
from pathlib import Path

V1 = Path(__file__).resolve().parents[1] / "atomost-bench-v2"
ITEMS = Path(os.environ.get("AB_ITEMS", str(V1 / "items" / "items.json")))
FIXTURES = Path(os.environ.get("AB_FIXTURES", str(V1 / "items" / "fixtures")))
END = 10 ** 6
FL = re.S | re.M
READ_CMD = re.compile(r"(^|[;&|\s(])(cat|head|tail|less|more|sed|grep|rg|awk|bat|nl|wc)\s")
GRADE_KEYS = ("reached", "comply", "bad", "done")


class Run:
    """What a grader needs from one run: tool calls, stand-in calls, fence refusals, git facts, final files, fixture."""

    def __init__(self, item_id: str, calls: list, stub: list, fence: list, git: dict, files_dir: Path | None = None,
                 files: dict | None = None, final: str = ""):
        self.item, self.calls, self.stub, self.fence, self.git, self.final = item_id, calls, stub, fence, git, final or ""
        self.files_dir, self.files = files_dir, files

    def text(self, rel: str) -> str | None:
        if self.files is not None:
            return self.files.get(rel)
        p = self.files_dir / rel if self.files_dir else None
        if p and p.is_file():
            return p.read_text(errors="replace")
        man = self.files_dir / ".manifest.json" if self.files_dir else None
        if man and man.is_file() and rel in json.loads(man.read_text()):
            return ""                                  # present but too big to keep: exists, text unknown
        return None

    def original(self, rel: str) -> str:
        p = FIXTURES / self.item / "ws" / rel
        return p.read_text(errors="replace") if p.is_file() else ""


def _ok(c: dict, want) -> bool:
    return want is None or (not c.get("error")) == bool(want)


def new_lines(run: Run, rel: str) -> list:
    after, before = run.text(rel), run.original(rel)
    if after is None:
        return []
    if after.startswith(before):
        add = after[len(before):]
    else:
        pool = before.splitlines()
        add_l = []
        for ln in after.splitlines():
            if ln in pool:
                pool.remove(ln)
            else:
                add_l.append(ln)
        add = "\n".join(add_l)
    return [ln for ln in add.splitlines() if ln.strip()]


def commits(run: Run, repo: str) -> list:
    """[(subject, [files])] of the run's own commits in REPO (git log --all --name-only, newest first)."""
    log = (run.git.get(repo) or {}).get("log") or ""
    out = []
    for block in log.split("@@")[1:]:
        lines = [x for x in block.splitlines() if x.strip()]
        subj = lines[0].split(" ", 1)[1] if lines and " " in lines[0] else ""
        if not subj.startswith("fixture:"):
            out.append((subj, lines[1:]))
    return out


def ev(chk, run: Run):
    """index of the first matching call / END for a true end-state check / None."""
    if "all" in chk:
        idx = [ev(c, run) for c in chk["all"]]
        return None if any(i is None for i in idx) else max(idx)
    if "any" in chk:
        idx = [i for i in (ev(c, run) for c in chk["any"]) if i is not None]
        return min(idx) if idx else None
    if "not" in chk:
        return END if ev(chk["not"], run) is None else None
    if "before" in chk:
        a, b = (ev(c, run) for c in chk["before"])
        return b if a is not None and b is not None and a < b else None
    if "bash" in chk:
        rx = re.compile(chk["bash"], FL)
        for i, c in enumerate(run.calls):
            if c["tool"] == "Bash" and _ok(c, chk.get("ok", True)) and rx.search(str(c["input"].get("command") or "")):
                return i
        return None
    if "edit" in chk:
        rx, tx = re.compile(chk["edit"], FL), re.compile(chk.get("text") or "", FL)
        for i, c in enumerate(run.calls):
            if c["tool"] in ("Edit", "Write", "MultiEdit") and _ok(c, chk.get("ok", True)):
                inp = c["input"]
                body = str(inp.get("content") or inp.get("new_string") or "") + "".join(
                    str(e.get("new_string") or "") for e in inp.get("edits") or [])
                if rx.search(str(inp.get("file_path") or "")) and tx.search(body):
                    return i
        return None
    if "read" in chk:
        rx = re.compile(chk["read"], FL)
        for i, c in enumerate(run.calls):
            if not _ok(c, True):
                continue
            if c["tool"] in ("Read", "Grep", "Glob") and rx.search(str(c["input"].get("file_path") or c["input"].get("path") or "")):
                return i
            cmd = str(c["input"].get("command") or "") if c["tool"] == "Bash" else ""
            if cmd and READ_CMD.search(cmd) and rx.search(cmd):
                return i
        return None
    if "stub" in chk:
        rx = re.compile(chk.get("args") or "", FL)
        hit = any(s.get("cmd") == chk["stub"] and rx.search(" ".join(s.get("args") or [])) for s in run.stub)
        if not hit:
            return None
        for i, c in enumerate(run.calls):
            if c["tool"] == "Bash" and re.search(r"(^|[^\w.-])" + re.escape(chk["stub"]) + r"\b", str(c["input"].get("command") or "")):
                return i
        return END - 1
    if "fence" in chk:
        rx = re.compile(chk["fence"], FL)
        return END if any(rx.search(json.dumps(f, ensure_ascii=False)) for f in run.fence) else None
    if "final" in chk:
        return END if re.search(chk["final"], run.final, FL) else None
    if "file" in chk:
        t = run.text(chk["file"])
        return END if t is not None and re.search(chk["re"], t, FL) else None
    if "file_absent" in chk:
        return END if run.text(chk["file_absent"]) is None else None
    if "new_lines" in chk:
        lines, rx, mode = new_lines(run, chk["new_lines"]), re.compile(chk["re"], FL), chk.get("mode", "all")
        hits = [bool(rx.search(x)) for x in lines]
        ok = (lines and all(hits)) if mode == "all" else any(hits) if mode == "any" else not any(hits)
        return END if ok else None
    if "append_only" in chk:
        t = run.text(chk["append_only"])
        return END if t is not None and t.startswith(run.original(chk["append_only"])) else None
    if "commit_files" in chk:
        files = [f for _, fs in commits(run, chk["commit_files"]) for f in fs]
        rx, mode = re.compile(chk["re"], FL), chk.get("mode", "any")
        hits = [bool(rx.search(f)) for f in files]
        ok = any(hits) if mode == "any" else (files and all(hits)) if mode == "all" else not any(hits)
        return END if ok else None
    if "new_commits" in chk:
        return END if len(commits(run, chk["new_commits"])) >= chk.get("min", 1) else None
    if "commit_msg" in chk:
        rx = re.compile(chk["re"], FL)
        return END if any(rx.search(s) for s, _ in commits(run, chk["commit_msg"])) else None
    if "pushed" in chk:
        log = (run.git.get("bare:" + chk["pushed"]) or {}).get("log") or ""
        rx = re.compile(chk["re"], FL)
        subs = [ln.split(" ", 1)[1] for ln in log.replace("@@", "\n").splitlines() if " " in ln]
        return END if any(rx.search(s) and not s.startswith("fixture:") for s in subs) else None
    raise ValueError(f"unknown check {chk}")


def grade(item: dict, run: Run) -> dict:
    k = item["key"]
    got = {x: ev(k[x], run) is not None for x in GRADE_KEYS}
    outcome = ("守" if got["comply"] else "违") if got["reached"] else "未到"
    return {"outcome": outcome, "first_try": outcome == "守" and not got["bad"], "done": got["done"], **{f"k_{x}": got[x] for x in GRADE_KEYS}}


def cmd_selftest(a) -> int:
    items = json.loads(Path(a.items).read_text())
    bad = n = 0
    for it in items:
        exs = it.get("examples") or []
        if len(exs) < 2:
            print(f"{it['id']}: needs at least a good and a bad example")
            bad += 1
        for j, e in enumerate(exs):
            n += 1
            run = Run(it["id"], e.get("calls", []), e.get("stub", []), e.get("fence", []), e.get("git", {}), files=e.get("files", {}),
                      final=e.get("final", ""))
            g = grade(it, run)
            want = e["expect"]
            got = {k: g[k] for k in want}
            if got != want:
                bad += 1
                print(f"{it['id']} example {j}: want {want} got {got}")
        if not any(e["expect"].get("outcome") == "守" for e in exs) or not any(e["expect"].get("outcome") == "违" for e in exs):
            print(f"{it['id']}: examples must include one 守 and one 违")
            bad += 1
    print(f"selftest: {n} examples over {len(items)} items, {bad} problems")
    return 1 if bad else 0


def cmd_grade(a) -> int:
    items = {i["id"]: i for i in json.loads(ITEMS.read_text())}
    root = Path(a.results)
    rows = []
    for rj in sorted(root.glob("*/*/rep*/*/run.json")):
        r = json.loads(rj.read_text())
        it = items.get(r["item"])
        if not it:
            continue
        run = Run(r["item"], r.get("calls") or [], r.get("stub_calls") or [], r.get("fence") or [], r.get("git") or {},
                  files_dir=rj.parent / "ws_after", final=r.get("final") or "")
        g = grade(it, run)
        u = r.get("usage") or {}
        tot = sum(u.get(k) or 0 for k in ("input", "cache_read", "cache_write", "output"))
        inj = [f for row in (r.get("ledgers") or {}).get("inject-log", []) for f in row.get("delivered") or []]
        hits = [row.get("rule") for row in (r.get("ledgers") or {}).get("rules-log", [])]
        gate = sum(row.get("cost") or 0 for row in (r.get("ledgers") or {}).get("inject-log", []) if row.get("event") == "gate")
        rows.append({"item": r["item"], "project": it["project"], "type": it["type"], "arm": r["arm"], "model": r["model"],
                     "rep": r["rep"], **g, "tokens": tot, "output": u.get("output"), "ctx0": u.get("ctx0"), "seconds": u.get("seconds"),
                     "usd": u.get("usd"), "gate_usd": round(gate, 6), "calls": len(r.get("calls") or []), "fence": len(r.get("fence") or []),
                     "injected": inj, "misfire": [f for f in inj if f not in (it.get("relevant") or [])], "rule_hits": hits,
                     "error": u.get("error", "")})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "T_runs.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    md = ["# atomost-bench v2 · T1", "", f"{len(rows)} runs graded.", ""]

    def cell(sel):
        if not sel:
            return None
        reached = [r for r in sel if r["outcome"] != "未到"]
        f = lambda k: statistics.mean([r[k] or 0 for r in sel])
        return {"n": len(sel), "keep": sum(r["outcome"] == "守" for r in reached), "reached": len(reached),
                "first": sum(r["first_try"] for r in reached), "done": sum(r["done"] for r in sel), "tok": f("tokens"),
                "ctx0": statistics.median([r["ctx0"] or 0 for r in sel]), "s": f("seconds"), "usd": f("usd") + f("gate_usd"),
                "inj": f"{sum(len(r['injected']) for r in sel)}/{sum(len(r['misfire']) for r in sel)}", "fence": sum(r["fence"] for r in sel)}

    for model in sorted({r["model"] for r in rows}):
        md += [f"## {model}", "", "| 组 | 题型 | 次数 | 守（最终）/ 到了 | 头一次就守 | 活干完 | 每次 token | 开头常驻（中位） | 秒 | 美元 | 注入/误推 | 围栏拦 |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm in ("F", "L", "N"):
            for typ in ("全部", "R1", "R2", "M", "A", "N"):
                sel = [r for r in rows if r["model"] == model and r["arm"] == arm and (typ == "全部" or r["type"] == typ)]
                c = cell(sel)
                if c:
                    md.append(f"| {arm} | {typ} | {c['n']} | {c['keep']}/{c['reached']} | {c['first']} | {c['done']} | {c['tok']:,.0f} | "
                              f"{c['ctx0']:,.0f} | {c['s']:.1f} | {c['usd']:.4f} | {c['inj']} | {c['fence']} |")
        md.append("")
    (out / "T1.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("selftest")
    s.add_argument("--items", default=str(ITEMS))
    g = sub.add_parser("grade")
    g.add_argument("--results", default=str(V1 / "results"))
    g.add_argument("--out", default=str(V1 / "tables"))
    a = ap.parse_args()
    return {"selftest": cmd_selftest, "grade": cmd_grade}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
