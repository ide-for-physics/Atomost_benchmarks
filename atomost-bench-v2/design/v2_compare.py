#!/usr/bin/env python3
"""atomost-bench v2 - compare v2 with v1, finding by finding (DESIGN.md section 4). Reads both graded tables
(tables/T_runs.json) and the run folders; writes tables/T2_compare.md. Arms F and N only (v2 has no L).

  per finding     the item it shows in, kept-of-3 per model x arm, v1 -> v2, and what happened in arm N:
                  did the fixed rule fire, did the memory arrive
  mis-pushes      injections the answer key calls off-topic, v1 -> v2; also without kernel-numerics in C03
                  (cophon strategist 10-27: picking smearing and grids is what C03 is about)
  log times       side measure over every run: lines appended to RUNNING.log / DECISION.log, how many carry a time
                  that is not the run's own clock (outside the run's wall-clock window, or no time at all)
    python3 v2_compare.py"""
import datetime as dt
import json
import re
from pathlib import Path

B = Path(__file__).resolve().parents[1]
V = {"v1": B / "atomost-bench-v1", "v2": B / "atomost-bench-v2"}
FIX = V["v2"] / "items" / "fixtures"                    # identical to v1's (checked at build)
ARMS, MODELS = ("F", "N"), ("haiku", "opus")
FINDINGS = [  # (finding, item, rule ids that should fire in N, memory that should arrive in N)
    ("1 发话里的相对路径触发注入", "M06", [], "tests-never-reach-real-claude.md"),
    ("2 多行循环的并发 ssh", "C05", ["ceci-no-parallel-ssh"], ""),
    ("4 碰集群前先读手册（拦一次）", "C04", ["hpc-handbook-before-clusters"], ""),
    ("5 带环境变量的 mpirun 走 heavy", "D04", ["heavy-for-local-heavy-work"], ""),
    ("6、7 EPW 输入的参数按规矩设", "C03", ["epw-input-param", "epw-input-by-shell"], ""),
]
TS = re.compile(r"^(\d{4}-\d\d-\d\d) (\d\d:\d\d)")


def load(v):
    return [r for r in json.loads((V[v] / "tables" / "T_runs.json").read_text()) if r["arm"] in ARMS]


def cell(rows, item, model, arm):
    rs = [r for r in rows if r["item"] == item and r["model"] == model and r["arm"] == arm]
    return sum(r["outcome"] == "守" for r in rs), rs


def log_times(v):
    """{arm: [appended lines, lines with no time or a time outside the run's window]} over all runs of version v."""
    c = {a: [0, 0] for a in ARMS}
    for rj in (V[v] / "results").glob("*/*/rep*/*/run.json"):
        r = json.loads(rj.read_text())
        if r["arm"] not in ARMS:
            continue
        end = dt.datetime.fromtimestamp(rj.stat().st_mtime)
        start = end - dt.timedelta(seconds=(r.get("usage") or {}).get("seconds") or 0)
        lo, hi = start - dt.timedelta(minutes=2), end + dt.timedelta(minutes=2)
        for after in (rj.parent / "ws_after").rglob("*.log"):
            if after.name not in ("RUNNING.log", "DECISION.log"):
                continue
            before = FIX / r["item"] / "ws" / after.relative_to(rj.parent / "ws_after")
            old = before.read_text(errors="replace").splitlines() if before.is_file() else []
            new = after.read_text(errors="replace").splitlines()
            added = new[len(old):] if new[:len(old)] == old else [x for x in new if x not in set(old)]
            for line in (x for x in added if x.strip()):
                m = TS.match(line)
                t = dt.datetime.strptime(f"{m[1]} {m[2]}", "%Y-%m-%d %H:%M") if m else None
                c[r["arm"]][0] += 1
                c[r["arm"]][1] += not (t and lo <= t <= hi)
    return c


def main():
    rows = {v: load(v) for v in V}
    out = ["# atomost-bench v2 · 对 v1 逐条比（每格 = 3 次里守了几次）", ""]
    out += ["| v1 第几条 | 题 | 模型 | F v1→v2 | N v1→v2 | v2 N 组：规则响了几次 / 记忆送到几次 |", "|---|---|---|---|---|---|"]
    for name, item, rule_ids, mem in FINDINGS:
        for m in MODELS:
            f1, _ = cell(rows["v1"], item, m, "F")
            f2, _ = cell(rows["v2"], item, m, "F")
            n1, _ = cell(rows["v1"], item, m, "N")
            n2, rs = cell(rows["v2"], item, m, "N")
            fired = sum(any(h in rule_ids for h in r["rule_hits"]) for r in rs) if rule_ids else "-"
            got = sum(mem in r["injected"] for r in rs) if mem else "-"
            out.append(f"| {name} | {item} | {m} | {f1}→{f2} | {n1}→{n2} | {fired} / {got} |")
    out += ["", "## 误推（N 组）", "", "| | 送出 | 与题无关 | 去掉 C03 的 kernel-numerics |", "|---|---|---|---|"]
    for v in V:
        ns = [r for r in rows[v] if r["arm"] == "N"]
        inj = sum(len(r["injected"]) for r in ns)
        mis = sum(len(r["misfire"]) for r in ns)
        mis2 = mis - sum(r["item"] == "C03" and "kernel-numerics.md" in r["misfire"] for r in ns)
        out.append(f"| {v} | {inj} | {mis} ({mis / max(inj, 1):.0%}) | {mis2} ({mis2 / max(inj, 1):.0%}) |")
    out += ["", "## 附带：追加进日志的行，时间不是本次运行的钟点（F、N 全部运行）", "", "| | 组 | 追加行 | 没时间或时间不对 |", "|---|---|---|---|"]
    for v in V:
        for a, (n, bad) in log_times(v).items():
            out.append(f"| {v} | {a} | {n} | {bad} |")
    text = "\n".join(out) + "\n"
    (V["v2"] / "tables" / "T2_compare.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
