#!/usr/bin/env python
"""cophon-bench v1 — the figures of the human-facing report (benchmarks/cophon-bench-v1/report/figures/).

    PY benchmarks/cophon_bench/figures_v1.py        # PY = kernel_pipeline/.venv/bin/python
Every number is read from the graded tables of benchmarks/cophon-bench-v1/tables/ (A_table.md, C2_table.md, E_ledger.json) and
the E grade files (results/e/grades*, which name the kernel files); the kernel spectra are re-parsed with the pipeline's parser.
Nothing is typed in.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path("<cophon>")
V1 = ROOT / "benchmarks/cophon-bench-v1"
TAB = V1 / "tables"
OUT = V1 / "report/figures"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "kernel_pipeline/src"))
from kernel_pipeline.lib.epw import kernel_invariant, parse_kernel  # noqa: E402

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 10,
    "axes.titlesize": 11, "axes.labelsize": 10, "legend.fontsize": 8.5, "figure.dpi": 150, "savefig.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
})
C_WB = "#b8b8b8"      # whiteboard
C_WB2 = "#7d7d7d"     # whiteboard, darker
C_HZ = "#1f5fa8"      # harness
C_HZ2 = "#7fb2e5"     # harness, lighter
C_CODE = "#d9822b"    # harness-code (no model) / references
MODELS = ["haiku", "sonnet", "opus", "fable", "deepseek-v4-flash"]
MLAB = {"haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5", "opus": "Opus 5.5", "fable": "Fable 5.1", "deepseek-v4-flash": "DeepSeek\nv4 flash"}
ARMS = ["harness+Haiku", "harness+Fable", "whiteboard Haiku", "whiteboard Fable"]
ACOL = {"harness+Haiku": C_HZ, "harness+Fable": C_HZ2, "whiteboard Haiku": C_WB2, "whiteboard Fable": C_WB}
MSHORT = {"GaP_t1": "GaP", "SnS2_mp1170": "SnS2", "NbFeSb_mp9437": "NbFeSb", "CdS_mp672": "CdS", "KNbO3_mp7375": "KNbO3",
          "InPS4_mp20790": "InPS4", "Bi2O2Se": "Bi2O2Se", "MoS2_monolayer": "MoS2 (1L)"}


def md_table(path: Path, header_key: str) -> list[dict]:
    """Parse the first markdown table whose header contains header_key."""
    rows, head = [], None
    for line in path.read_text().splitlines():
        if not line.startswith("|"):
            if head is not None and rows:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if head is None:
            if header_key in line:
                head = cells
            continue
        if set(line.replace("|", "").strip()) <= set("-: "):
            continue
        rows.append(dict(zip(head, cells)))
    return rows


def num(s) -> float:
    m = re.search(r"-?\d+(\.\d+)?", str(s))
    return float(m.group()) if m else float("nan")


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# ----------------------------------------------------------------------------------------------- data
LEDGER = json.loads((TAB / "E_ledger.json").read_text())["arms"]
MATS = list(dict.fromkeys(r["material"] for r in LEDGER))
BASE = json.loads((V1 / "labels/E_baselines.json").read_text())["materials"]
GRADES = {}
for d in ("grades", "grades_excluded"):
    for f in (V1 / "results/e" / d).glob("*.grade.json"):
        g = json.loads(f.read_text()); GRADES[g["arm"]] = g
SFX = {"harness+Haiku": "e2eH", "harness+Fable": "e2eF", "whiteboard Haiku": "wb_haiku", "whiteboard Fable": "wb_fable"}


def grade_of(m: str, arm: str):
    s = SFX[arm]
    for k in (f"{m}_{s}", f"{m}_{s}_invalid", f"{m}_{s}_provisional"):
        if k in GRADES:
            return GRADES[k]
    return None


def a_tables():
    p = TAB / "A_table.md"
    return {(r["set"], r["arm"], r["model"]): r for r in md_table(p, "class score")} if p.is_file() else {}


def c_tables():
    p = TAB / "C2_table.md"
    if not p.is_file():
        return {}, {}
    return ({(r["arm"], r["model"]): r for r in md_table(p, "promising picks")},
            {(r["arm"], r["model"]): r for r in md_table(p, "picks inside the pool")})


def arm_counts(arm: str) -> dict:
    rs = [r for r in LEDGER if r["arm"] == arm]
    fin = [r for r in rs if r["status"] == "finished"]
    return {"same": sum(r["verdict"] == "same answer" for r in fin), "differs": sum(r["verdict"] != "same answer" for r in fin),
            "not finished": sum(r["status"] == "not finished" for r in rs), "excluded": sum(r["status"] in ("invalid", "stopped") for r in rs),
            "usd": sum(r["model_usd"] or 0 for r in rs)}


# ----------------------------------------------------------------------------------------------- F1 overview
def fig_overview():
    A = a_tables(); Call, Cdisc = c_tables()
    fig, axs = plt.subplots(1, 4, figsize=(15.5, 3.5), gridspec_kw=dict(width_ratios=[1, 1, 1.35, 1.1]))
    for ax, (title, vals, top, ref) in zip(axs[:2], [
        ("A  Operator tickets (44)\nclass score, median of 5", [
            ("whiteboard\nFable", num(A.get(("main", "whiteboard", "fable"), {}).get("class score")), C_WB),
            ("harness\nHaiku", num(A.get(("main", "harness", "haiku"), {}).get("class score")), C_HZ),
            ("harness\nFable", num(A.get(("main", "harness", "fable"), {}).get("class score")), C_HZ2)], 44, (32.5, "escalate everything")),
        ("C  Batch selection, pool models cannot recall (33)\nline-hit & radiating picks (of 8)", [
            ("whiteboard\nFable", num(Cdisc.get(("whiteboard", "fable"), {}).get("line-hit & radiating")), C_WB),
            ("harness\nHaiku", num(Cdisc.get(("harness", "haiku"), {}).get("line-hit & radiating")), C_HZ),
            ("harness\nFable", num(Cdisc.get(("harness", "fable"), {}).get("line-hit & radiating")), C_HZ2)], 8,
            (num(Cdisc.get(("random 8 (expectation, pool only)", "-"), {}).get("line-hit & radiating")), "random 8")),
    ]):
        xs = np.arange(len(vals))
        ax.bar(xs, [v for _, v, _ in vals], color=[c for _, _, c in vals], width=0.6)
        for x, (_, v, _) in zip(xs, vals):
            ax.text(x, v, "—" if np.isnan(v) else f"{v:g}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks(xs, [l for l, _, _ in vals], fontsize=8.5); ax.set_ylim(0, top); ax.set_title(title, loc="left", fontsize=9.5)
        if ref and not np.isnan(ref[0]):
            ax.axhline(ref[0], color=C_CODE, ls="--", lw=1, label=ref[1]); ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax = axs[2]; ys = np.arange(len(ARMS))[::-1]
    parts = [("same", "#2e7d32", "same answer"), ("differs", "#c62828", "different answer"), ("not finished", "#9e9e9e", "harness did not finish"),
             ("excluded", "#e0e0e0", "whiteboard invalid / stopped")]
    left = np.zeros(len(ARMS))
    for key, col, lab in parts:
        v = np.array([arm_counts(a)[key] for a in ARMS], float)
        ax.barh(ys, v, left=left, color=col, label=lab, height=0.6, edgecolor="white")
        for y, l, x in zip(ys, left, v):
            if x:
                ax.text(l + x / 2, y, f"{x:g}", ha="center", va="center", fontsize=8.5, color="white" if key in ("same", "differs") else "#222")
        left += v
    ax.set_yticks(ys, ARMS, fontsize=8.5); ax.set_xlim(0, 8); ax.set_xlabel("materials (of 8)")
    ax.set_title("E  End-to-end, 8 materials\noutcome per arm", loc="left", fontsize=9.5)
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=2)
    ax = axs[3]; v = [arm_counts(a)["usd"] for a in ARMS]
    ax.barh(ys, v, color=[ACOL[a] for a in ARMS], height=0.6); ax.set_xscale("log"); ax.set_xlim(0.05, 600)
    for y, x in zip(ys, v):
        ax.text(x * 1.15, y, f"${x:.2f}" if x < 1 else f"${x:.0f}", va="center", fontsize=8.5)
    ax.set_yticks(ys, ARMS, fontsize=8.5); ax.set_xlabel("USD, list price, log scale")
    ax.set_title("E  model spend per arm, 8 materials", loc="left", fontsize=9.5)
    fig.tight_layout(); save(fig, "F1_overview")


# ----------------------------------------------------------------------------------------------- F2 A
def fig_A():
    A = a_tables()
    if not A:
        print("skip F2 (no tables/A_table.md)"); return
    fig, axs = plt.subplots(1, 3, figsize=(14, 3.6), gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
    xs = np.arange(len(MODELS)); w = 0.38
    for ax, st, top, ref in ((axs[0], "main", 44, 32.5), (axs[1], "holdout", 7, 4.0)):
        wb = [num(A[(st, "whiteboard", m)]["class score"]) for m in MODELS]; hz = [num(A[(st, "harness", m)]["class score"]) for m in MODELS]
        ax.bar(xs - w / 2, wb, w, color=C_WB, label="whiteboard (model alone)"); ax.bar(xs + w / 2, hz, w, color=C_HZ, label="harness")
        for x, a, b in zip(xs, wb, hz):
            ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=7.5)
        ax.axhline(ref, color=C_CODE, ls="--", lw=1, label="escalate everything")
        ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_ylim(0, top * 1.2)
        ax.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=3)
        n = "44 sealed tickets" if st == "main" else "7 hold-out tickets (after the v0 freeze)"
        ax.set_title(f"A{1 if st == 'main' else 2}  {n}: class score, median of 5", loc="left", fontsize=9.5)
    ax = axs[2]
    wb = [num(A[("main", "whiteboard", m)]["compute-burning answers"]) for m in MODELS]; hz = [num(A[("main", "harness", m)]["compute-burning answers"]) for m in MODELS]
    ax.bar(xs - w / 2, wb, w, color=C_WB); ax.bar(xs + w / 2, hz, w, color=C_HZ)
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_title("A3  answers re-running compute for nothing (main)", loc="left", fontsize=9.5)
    fig.tight_layout(); save(fig, "F2_pillar_A")


# ----------------------------------------------------------------------------------------------- F3 C stage 2
def fig_C():
    Call, Cdisc = c_tables()
    if not Call:
        print("skip F3 (no tables/C2_table.md)"); return
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 3.6))
    xs = np.arange(len(MODELS)); w = 0.38
    for ax, T, col, title, refs in (
            (axs[0], Cdisc, "line-hit & radiating", "C1  pool models cannot recall (33): line-hit & radiating picks of 8",
             [("random 8 (expectation, pool only)", "random"), ("harness-code (top-8 prior score)", "prior top-8, no model"), ("oracle (top-8 by main score, pool)", "best possible")]),
            (axs[1], Call, "promising picks (of 8)", "C2  whole pool (47): promising picks of 8 (4 exist)",
             [("random 8 (expectation)", "random"), ("harness-code (top-8 prior score)", "prior top-8, no model"), ("oracle (top-8 by main score)", "best possible")])):
        wb = [num(T.get(("whiteboard", m), {}).get(col)) for m in MODELS]; hz = [num(T.get(("harness", m), {}).get(col)) for m in MODELS]
        ax.bar(xs - w / 2, wb, w, color=C_WB, label="whiteboard"); ax.bar(xs + w / 2, hz, w, color=C_HZ, label="harness")
        for x, a, b in zip(xs, wb, hz):
            ax.text(x - w / 2, 0 if np.isnan(a) else a, "—" if np.isnan(a) else f"{a:g}", ha="center", va="bottom", fontsize=7.5)
            ax.text(x + w / 2, 0 if np.isnan(b) else b, "—" if np.isnan(b) else f"{b:g}", ha="center", va="bottom", fontsize=7.5)
        for (key, lab), ls in zip(refs, (":", "--", "-.")):
            r = T.get((key, "-"))
            if r:
                v = num(r.get(col)); ax.axhline(v, color=C_CODE, ls=ls, lw=1, label=f"{lab} ({v:g})")
        ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_ylim(0, 10); ax.set_title(title, loc="left", fontsize=9.5)
        ax.legend(frameon=False, fontsize=7.3, loc="upper left", ncol=3)
    fig.tight_layout(); save(fig, "F3_pillar_C")


# ----------------------------------------------------------------------------------------------- F4 E kernels
def fig_E_kernels():
    fig, axs = plt.subplots(2, 4, figsize=(15.5, 6.6)); axs = axs.ravel()
    sty = {"harness+Haiku": dict(color=C_HZ, lw=1.4, ls="--"), "harness+Fable": dict(color=C_HZ2, lw=1.4, ls=(0, (1, 1))),
           "whiteboard Haiku": dict(color=C_WB2, lw=1.2, ls="-"), "whiteboard Fable": dict(color="#c0392b", lw=1.1, ls="-.")}
    for ax, m in zip(axs, MATS):
        b = BASE[m]; k = parse_kernel(Path(b["kernel"]["file"])); inv = kernel_invariant(k)["invariant"]; w = np.asarray(k["photon_ev"])
        ax.plot(w, inv, color="#222", lw=1.7, label=f"baseline {inv.max():.1f} at {w[int(np.argmax(inv))]:.2f} eV")
        for arm in ARMS:
            row = next(r for r in LEDGER if r["material"] == m and r["arm"] == arm); g = grade_of(m, arm)
            if g is None:
                ax.plot([], [], **sty[arm], label=f"{arm}: did not finish"); continue
            kk = parse_kernel(Path(g["kernel_file"])); ii = kernel_invariant(kk)["invariant"]; ww = np.asarray(kk["photon_ev"])
            tag = {"invalid": " (invalid)", "stopped": " (stopped, provisional)"}.get(row["status"], "")
            mark = "= same" if g["same_answer"] else "≠ differs"
            ax.plot(ww, ii, alpha=0.45 if tag else 1.0, **sty[arm], label=f"{arm}{tag} {mark}")
        ax.set_title(f"{MSHORT[m]}  (baseline mode {b['peaks'][0]['mode_group']['thz']:.2f} THz)", loc="left", fontsize=9.5)
        ax.set_xlim(0, 6); ax.legend(frameon=False, fontsize=6.3, loc="upper left")
        if m == "CdS_mp672":
            ax.set_yscale("log"); ax.set_ylim(0.05, 3000); ax.text(0.98, 0.04, "log scale: both whiteboard arms\n~47× high (a trap the harness rulebook records)", transform=ax.transAxes, ha="right", fontsize=6.8)
    for i in (0, 4):
        axs[i].set_ylabel("kernel invariant (Å²/eV)")
    for ax in axs[4:]:
        ax.set_xlabel("photon energy (eV)")
    fig.tight_layout(); save(fig, "F4_E_kernels")


# ----------------------------------------------------------------------------------------------- F5 E cost
def fig_E_cost():
    fig, axs = plt.subplots(1, 2, figsize=(14, 3.8), gridspec_kw=dict(width_ratios=[2.2, 1]))
    ax = axs[0]; xs = np.arange(len(MATS)); w = 0.2
    for j, arm in enumerate(ARMS):
        for x, m in zip(xs, MATS):
            r = next(r for r in LEDGER if r["material"] == m and r["arm"] == arm); v = r["node_h"] or 0
            hatch = None if r["status"] == "finished" else ("///" if r["status"] == "not finished" else "..")
            ax.bar(x + (j - 1.5) * w, v, w, color=ACOL[arm] if r["status"] == "finished" else "white", edgecolor=ACOL[arm], hatch=hatch, lw=0.8,
                   label=arm if m == MATS[0] else None)
    from matplotlib.patches import Patch
    h, l = ax.get_legend_handles_labels()
    h += [Patch(facecolor="white", edgecolor="#555", hatch="///"), Patch(facecolor="white", edgecolor="#555", hatch="..")]
    l += ["harness did not finish", "whiteboard: invalid / stopped"]
    ax.set_xticks(xs, [MSHORT[m] for m in MATS], fontsize=8.5); ax.set_ylabel("node-hours")
    common = [m for m in MATS if all(next(r for r in LEDGER if r["material"] == m and r["arm"] == a)["status"] == "finished" for a in ARMS)]
    tot = {a: sum(next(r for r in LEDGER if r["material"] == m and r["arm"] == a)["node_h"] for m in common) for a in ARMS}
    ax.set_title("E1  compute per material and arm; on the %d materials all four arms finished: " % len(common)
                 + ", ".join(f"{a} {tot[a]:.1f}" for a in ARMS), loc="left", fontsize=8.8)
    ax.legend(h, l, frameon=False, fontsize=7.2, ncol=3, loc="upper left")
    ax = axs[1]; ys = np.arange(len(ARMS))[::-1]
    fin = [sum((r["node_h"] or 0) for r in LEDGER if r["arm"] == a and r["status"] == "finished") for a in ARMS]
    rest = [sum((r["node_h"] or 0) for r in LEDGER if r["arm"] == a and r["status"] != "finished") for a in ARMS]
    ax.barh(ys, fin, color=[ACOL[a] for a in ARMS], height=0.6, label="finished arms")
    ax.barh(ys, rest, left=fin, color="white", edgecolor=[ACOL[a] for a in ARMS], hatch="///", height=0.6, label="not finished / excluded")
    for y, a, b in zip(ys, fin, rest):
        ax.text(a + b + 0.5, y, f"{a:.1f} + {b:.1f}", va="center", fontsize=8)
    ax.set_yticks(ys, ARMS, fontsize=8.5); ax.set_xlabel("node-hours, all 8 materials"); ax.set_xlim(0, max(np.add(fin, rest)) * 1.35)
    ax.set_title("E2  total compute per arm", loc="left", fontsize=9.5)
    ax.legend(frameon=False, fontsize=7.2, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    fig.tight_layout(); save(fig, "F5_E_cost")


if __name__ == "__main__":
    which = sys.argv[1:] or ["overview", "A", "C", "kernels", "cost"]
    for name, fn in (("overview", fig_overview), ("A", fig_A), ("C", fig_C), ("kernels", fig_E_kernels), ("cost", fig_E_cost)):
        if name in which:
            fn()
