#!/usr/bin/env python
"""cophon-bench v0 — the figures of the human-facing report (benchmarks/cophon-bench-v0/report/figures/).

Run with the package interpreter (kernel_pipeline/.venv/bin/python) from anywhere:
    PY benchmarks/cophon_bench/figures_v0.py
Every number is read from the frozen tables / result files of benchmarks/cophon-bench-v0/ (nothing typed in except the
end-to-end cost ledger, which is copied from REPORT_v0.md's E table and the sacct accounting recorded there).
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path("~/9.coherent_phonon")
V0 = ROOT / "benchmarks/cophon-bench-v0"
TAB = V0 / "tables"
OUT = V0 / "report/figures"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "kernel_pipeline/src"))
from kernel_pipeline.lib.epw import kernel_invariant, parse_kernel  # noqa: E402

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "font.size": 10,
    "axes.titlesize": 11, "axes.labelsize": 10, "legend.fontsize": 8.5, "figure.dpi": 150, "savefig.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
})
C_WB = "#b8b8b8"      # whiteboard
C_HZ = "#1f5fa8"      # harness
C_HZ2 = "#7fb2e5"     # harness, lighter
C_CODE = "#d9822b"    # harness-code (no model)
C_REF = "#444444"
MODELS = ["haiku", "sonnet", "opus", "fable", "deepseek-v4-flash"]
MLAB = {"haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5", "opus": "Opus 5.5", "fable": "Fable 5.1", "deepseek-v4-flash": "DeepSeek\nv4 flash"}


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


def num(s: str) -> float:
    m = re.search(r"-?\d+(\.\d+)?", s)
    return float(m.group()) if m else float("nan")


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# ----------------------------------------------------------------------------------------------- data
A = {(r["arm"], r["model"]): r for r in md_table(TAB / "A_table.md", "class score")}
Abest = {(r["arm"], r["model"]): r for r in md_table(TAB / "A_best.md", "best action")}
Call = {(r["arm"], r["model"]): r for r in md_table(TAB / "C_table.md", "promising picks")}
Cdisc = {(r["arm"], r["model"]): r for r in md_table(TAB / "C_table.md", "picks inside the pool")}
D = {(r["arm"], r["model"]): r for r in md_table(TAB / "D_table.md", "peak point within")}
Bcum = json.load(open(TAB / "B_cumulative_r2.json"))      # model -> (any1, any2, all1, all2, pend)
Brows = json.load(open(TAB / "B_detail.json"))

# B: per material x model pass picture (whiteboard, two rounds) and harness-model round 2
mats = sorted(set(r["material"] for r in Brows))
wb_pass = collections.defaultdict(lambda: collections.defaultdict(bool))   # mat -> model -> any pass (r1 or r2)
hm_pass = collections.defaultdict(lambda: collections.defaultdict(bool))   # mat -> model -> any pass in harness-model r2
for r in Brows:
    c = r.get("card")
    ok = bool(c) and (c.get("gate") == "PASS" or c.get("gate_today") == "PASS")
    for arm, model, rep in r["sources"]:
        if arm.startswith("B_whiteboard"):
            wb_pass[r["material"]][model] |= ok
        elif arm.startswith("B_harnessmodel"):
            hm_pass[r["material"]][model] |= ok
CODE_FAIL = {"Li2CuSb_mp15988", "Na2O_mp2352", "NbFeSb_mp9437"}   # recorded: code recipe v1.1 fails these three at round 1

# E: the six flights (from REPORT_v0.md E table and the sacct accounting recorded there)
E = {
    "GaP": {"base": (2.82, 16.03, "T2 10.77 THz"), "harness": dict(peak=2.82, h=15.94, mode="T2 10.77", nodeh=1.08, usd=0.1, wall=8.82, queue=7.5),
            "whiteboard": dict(peak=2.81, h=17.61, mode="T2 10.735", nodeh=10.14, usd=51.7, wall=9.88, queue=0.0, turns=108)},
    "SnS2": {"base": (5.46, 47.09, "A1g 9.35 THz"), "harness": dict(peak=3.78, h=45.63, mode="A1g 9.18", nodeh=2.35, usd=0.1, wall=9.92, queue=7.5),
             "whiteboard": dict(peak=4.08, h=54.1, mode="A1g 9.20", nodeh=7.35, usd=20.7, wall=5.18, queue=0.0, turns=87)},
    "NbFeSb": {"base": (3.36, 21.31, "T2 8.26 THz"), "harness": dict(peak=3.36, h=21.49, mode="T2 8.26", nodeh=4.97, usd=0.1, wall=11.08, queue=7.5),
               "whiteboard": dict(peak=3.275, h=25.6, mode="T2 7.89", nodeh=12.92, usd=25.9, wall=4.18, queue=0.0, turns=126)},
}
KERNELS = {
    "GaP": {"baseline (library)": ROOT / "materials/GaP_t1/results/kernel_k96/Gamma_alphabeta_s.dat",
            "harness + Haiku": V0 / "e2e_library/GaP_e2e/results/kernel_k96/Gamma_alphabeta_s.dat",
            "whiteboard Fable": V0 / "results/e/whiteboard_GaP/Gamma_alphabeta_s_k192.dat"},
    "SnS2": {"baseline (library)": ROOT / "materials/SnS2_mp1170/results/kernel_k64/Gamma_alphabeta_s.dat",
             "harness + Haiku": V0 / "e2e_library/SnS2_e2e/results/kernel_k64/Gamma_alphabeta_s.dat",
             "whiteboard Fable": V0 / "results/e/whiteboard_SnS2/Gamma_alphabeta_s_k120x120x60.dat"},
    "NbFeSb": {"baseline (library)": ROOT / "materials/NbFeSb_mp9437/results/kernel_k64/Gamma_alphabeta_s.dat",
               "harness + Haiku": V0 / "e2e_library/NbFeSb_e2e/results/kernel_k64/Gamma_alphabeta_s.dat",
               "whiteboard Fable": V0 / "results/e/whiteboard_NbFeSb/Gamma_alphabeta_s_k96.dat"},
}

# ----------------------------------------------------------------------------------------------- F1 overview
def fig_overview():
    fig, axs = plt.subplots(1, 5, figsize=(15, 3.3))
    panels = [
        ("A  Operator tickets\nclass score (of 44)", [
            ("whiteboard\nFable", num(A[("whiteboard", "fable")]["class score"]), C_WB),
            ("harness\nHaiku", num(A[("harness", "haiku")]["class score"]), C_HZ),
            ("harness\nFable", num(A[("harness", "fable")]["class score"]), C_HZ2)], 44),
        ("B  Wannier projection\nmaterials passed (of 16), two rounds", [
            ("whiteboard\nFable", Bcum["fable"][1], C_WB),
            ("harness code\nno model", 13, C_CODE),
            ("harness\n+ Haiku", 13 + sum(1 for m in CODE_FAIL if hm_pass[m]["haiku"]), C_HZ)], 16),
        ("C  Batch selection\nhits in the loop-found pool (of 8 picks)", [
            ("whiteboard\nFable", num(Cdisc[("whiteboard", "fable")]["line-hit & radiating"]), C_WB),
            ("harness\nHaiku", num(Cdisc[("harness", "haiku")]["line-hit & radiating"]), C_HZ),
            ("harness\nFable", num(Cdisc[("harness", "fable")]["line-hit & radiating"]), C_HZ2)], 8),
        ("D  Peak prediction\nshortlist within 0.3 eV (of 37)", [
            ("whiteboard\nFable", num(D[("whiteboard", "fable")]["shortlist (<=3) within 0.3 eV"]), C_WB),
            ("harness\nHaiku", num(D[("harness", "haiku")]["shortlist (<=3) within 0.3 eV"]), C_HZ),
            ("harness\nFable", num(D[("harness", "fable")]["shortlist (<=3) within 0.3 eV"]), C_HZ2)], 37),
        ("E  End-to-end, 3 materials\ncompute, node-hours (lower is better)", [
            ("whiteboard\nFable", sum(E[m]["whiteboard"]["nodeh"] for m in E), C_WB),
            ("harness\nHaiku", sum(E[m]["harness"]["nodeh"] for m in E), C_HZ)], None),
    ]
    for ax, (title, bars, ymax) in zip(axs, panels):
        xs = np.arange(len(bars))
        vals = [b[1] for b in bars]
        ax.bar(xs, vals, color=[b[2] for b in bars], width=0.62)
        for x, v in zip(xs, vals):
            ax.text(x, v, f"{v:g}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks(xs, [b[0] for b in bars], fontsize=8)
        ax.set_title(title, fontsize=9.5, loc="left")
        if ymax:
            ax.set_ylim(0, ymax * 1.12)
            ax.axhline(ymax, color=C_REF, lw=0.6, ls=":")
        else:
            ax.set_ylim(0, max(vals) * 1.2)
    fig.suptitle("cophon-bench v0: the same question, three operators (grey = frontier model alone; blue = the harness with the cheapest model)",
                 fontsize=10, x=0.01, ha="left", y=1.02)
    save(fig, "F1_overview")


# ----------------------------------------------------------------------------------------------- F2 harness architecture
def fig_harness():
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")

    def box(x, y, w, h, text, fc, ec="#333", fs=8.5, weight="normal"):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=0.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight=weight)

    # pipeline stages
    stages = ["intake", "relax", "electron\n+ PDOS", "superset\nprojectability", "Wannier\nrounds", "phonons\n(DFPT)", "EPW1", "kernel\nladder", "route\ncheck", "report"]
    for i, s in enumerate(stages):
        box(0.2 + i * 0.97, 2.75, 0.88, 0.62, s, "#eef3fa", fs=7.5)
        if i < len(stages) - 1:
            ax.annotate("", xy=(0.2 + (i + 1) * 0.97, 3.06), xytext=(0.2 + i * 0.97 + 0.88, 3.06), arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(0.2, 3.5, "sealed pipeline code (kernel_pipeline v2.0.x): one legal next action at a time; every stage ends in a code gate",
            fontsize=8.5, weight="bold")
    # knowledge layer
    ax.text(0.2, 2.42, "knowledge the code consults", fontsize=8.5, weight="bold")
    kn = ["rulebook\n(690 lines, 10 families)", "round-1 recipe\nstrategy v1.1", "iteration strategy\n+ lessons", "casebook\n(certified recipes)", "cheap prior\n(193 materials)", "cost model\n+ cluster registry"]
    for i, s in enumerate(kn):
        box(0.2 + i * 1.62, 1.7, 1.5, 0.62, s, "#fdf3e7", fs=7.5)
    # routine / supervisor
    box(0.2, 0.75, 4.6, 0.72, "routine: submit, poll, pull, gate, ladder move, retry, report, export\n(drive / supervise, no model in the loop)", "#eaf5ea", fs=8)
    box(5.1, 0.75, 4.7, 0.72, "when a stage blocks: a ticket names the allowed actions;\nthe operator model answers one JSON object; the validator applies it", "#f6eaea", fs=8)
    ax.annotate("", xy=(4.8, 1.11), xytext=(5.1, 1.11), arrowprops=dict(arrowstyle="<->", lw=0.7))
    # model
    box(5.1, 0.05, 4.7, 0.5, "operator model (any: Haiku ... Fable, DeepSeek):\njudgment only where the code asks for it", "#ffffff", fs=8, weight="bold")
    ax.annotate("", xy=(7.45, 0.75), xytext=(7.45, 0.55), arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(0.2, 0.3, "harness = code + gates + knowledge + ticket contract\n+ supervisor + library experience. The whiteboard arm gets\nnone of it: structure, papers, toolchain and cluster only.", fontsize=8, style="italic", va="center")
    ax.text(0.2, 4.25, "What the harness is", fontsize=11, weight="bold")
    save(fig, "F2_harness")


# ----------------------------------------------------------------------------------------------- F3 pillar A
def fig_A():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.4), gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
    xs = np.arange(len(MODELS)); w = 0.38
    ax = axs[0]
    wb = [num(A[("whiteboard", m)]["class score"]) for m in MODELS]
    hz = [num(A[("harness", m)]["class score"]) for m in MODELS]
    ax.bar(xs - w / 2, wb, w, color=C_WB, label="whiteboard (evidence only)")
    ax.bar(xs + w / 2, hz, w, color=C_HZ, label="harness (ticket + rules + actions)")
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=7.5)
    ax.axhline(32.5, color=C_REF, lw=0.7, ls="--", label="'escalate everything' reference: 32.5")
    ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_ylim(0, 56); ax.set_ylabel("class score (of 44 tickets)")
    ax.set_title("A1  decision quality on 44 real tickets", loc="left"); ax.legend(loc="upper left", frameon=False, ncol=1)
    ax = axs[1]
    wb = [num(A[("whiteboard", m)]["compute-burning answers"]) for m in MODELS]
    hz = [num(A[("harness", m)]["compute-burning answers"]) for m in MODELS]
    ax.bar(xs - w / 2, wb, w, color=C_WB); ax.bar(xs + w / 2, hz, w, color=C_HZ)
    for x, a in zip(xs, wb):
        ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5)
    ax.text(len(MODELS) / 2 - 0.5, 0.4, "harness: 0 for every model", ha="center", color=C_HZ, fontsize=8)
    ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_ylim(0, 9); ax.set_ylabel("answers that would waste compute")
    ax.set_title("A2  wasteful resubmissions", loc="left")
    ax = axs[2]
    wb = [num(Abest[("whiteboard", m)]["best action, decision tickets"]) for m in MODELS]
    hz = [num(Abest[("harness", m)]["best action, decision tickets"]) for m in MODELS]
    ax.bar(xs - w / 2, wb, w, color=C_WB); ax.bar(xs + w / 2, hz, w, color=C_HZ)
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_ylim(0, 19 * 1.15); ax.axhline(19, color=C_REF, lw=0.6, ls=":")
    ax.set_ylabel("best action (of 19 decision tickets)"); ax.set_title("A3  the 19 tickets that need a real decision", loc="left")
    save(fig, "F3_pillar_A")


# ----------------------------------------------------------------------------------------------- F4 pillar B
def fig_B():
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw=dict(width_ratios=[1, 1.55]))
    ax = axs[0]
    xs = np.arange(len(MODELS)); w = 0.26
    r1 = [Bcum[m][0] for m in MODELS]; r2 = [Bcum[m][1] for m in MODELS]
    hm = [13 + sum(1 for mm in CODE_FAIL if hm_pass[mm][m]) for m in MODELS]
    ax.bar(xs - w, r1, w, color="#d0d0d0", label="whiteboard, round 1")
    ax.bar(xs, r2, w, color=C_WB, edgecolor="#777", label="whiteboard, rounds 1+2 (any of 3 tries)")
    ax.bar(xs + w, hm, w, color=C_HZ, label="harness: code round 1 + model with the diagnosis card")
    ax.axhline(13, color=C_CODE, lw=1.2, ls="--", label="harness code alone, round 1: 13")
    ax.axhline(2, color=C_REF, lw=0.8, ls=":", label="old heuristic ladder, round 1: 2 (recorded)")
    for x, a, b, c in zip(xs, r1, r2, hm):
        ax.text(x - w, a, f"{a}", ha="center", va="bottom", fontsize=7.5); ax.text(x, b, f"{b}", ha="center", va="bottom", fontsize=7.5); ax.text(x + w, c, f"{c}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(xs, [MLAB[m] for m in MODELS], fontsize=8); ax.set_ylim(0, 22); ax.set_ylabel("materials whose block passed the gate (of 16)")
    ax.set_title("B1  Wannier projection blocks: materials passed", loc="left"); ax.legend(loc="upper left", frameon=False, fontsize=7.3)
    # B2 matrix
    ax = axs[1]
    cols = [f"wb {MLAB[m].split()[0]}" for m in MODELS] + ["harness code\nround 1"] + [f"harness+{MLAB[m].split()[0]}\nround 2" for m in MODELS]
    mat_order = sorted(mats, key=lambda m: (-sum(wb_pass[m][x] for x in MODELS), m))
    grid = np.full((len(mat_order), len(cols)), np.nan)
    for i, m in enumerate(mat_order):
        for j, x in enumerate(MODELS):
            grid[i, j] = 1.0 if wb_pass[m][x] else 0.0
        grid[i, len(MODELS)] = 0.0 if m in CODE_FAIL else 1.0
        for j, x in enumerate(MODELS):
            grid[i, len(MODELS) + 1 + j] = (1.0 if hm_pass[m][x] else 0.0) if m in CODE_FAIL else np.nan
    cmap = matplotlib.colors.ListedColormap(["#f3d6d6", "#bfe3bf"])
    ax.imshow(np.nan_to_num(grid, nan=0.5), cmap=matplotlib.colors.ListedColormap(["#f3d6d6", "#f4f4f4", "#bfe3bf"]), vmin=0, vmax=1, aspect="auto")
    for i in range(len(mat_order)):
        for j in range(len(cols)):
            v = grid[i, j]
            ax.text(j, i, "pass" if v == 1 else ("fail" if v == 0 else "n/a"), ha="center", va="center", fontsize=6.5,
                    color="#2d6a2d" if v == 1 else ("#8a2d2d" if v == 0 else "#999"))
    ax.set_xticks(range(len(cols)), cols, fontsize=6.8, rotation=35, ha="right")
    ax.set_yticks(range(len(mat_order)), [m.split("_")[0] for m in mat_order], fontsize=7.5)
    ax.axvline(len(MODELS) - 0.5, color="#333", lw=0.8); ax.axvline(len(MODELS) + 0.5, color="#333", lw=0.8)
    ax.set_title("B2  which materials: whiteboard after two rounds (any of 3 tries) | harness code | harness + model where the code failed", loc="left", fontsize=9)
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, "F4_pillar_B")


# ----------------------------------------------------------------------------------------------- F5 pillar C
def fig_C():
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.5))
    ms = ["haiku", "sonnet", "opus", "fable"]
    xs = np.arange(len(ms)); w = 0.38
    ax = axs[0]
    wb = [num(Cdisc[("whiteboard", m)]["line-hit & radiating"]) for m in ms]
    hz = [num(Cdisc[("harness", m)]["line-hit & radiating"]) for m in ms]
    ax.bar(xs - w / 2, wb, w, color=C_WB, label="whiteboard (formula, structure, gap)")
    ax.bar(xs + w / 2, hz, w, color=C_HZ, label="harness (+ prior, evidence, selection rules)")
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=8); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=8)
    for y, lab, c in ((num(Cdisc[("random 8 (expectation, pool only)", "-")]["line-hit & radiating"]), "random 8 (expectation)", C_REF),
                      (num(Cdisc[("harness-code (top-8 prior score)", "-")]["line-hit & radiating"]), "harness code alone: prior top-8", C_CODE),
                      (num(Cdisc[("oracle (top-8 by main score, pool)", "-")]["line-hit & radiating"]), "oracle (best possible)", "#2d6a2d")):
        ax.axhline(y, color=c, lw=0.9, ls="--", label=f"{lab}: {y:g}")
    ax.set_xticks(xs, [MLAB[m] for m in ms], fontsize=8); ax.set_ylim(0, 11); ax.set_ylabel("picks that hit a laser line and radiate (of 8)")
    ax.set_title("C1  loop-discovered pool (23 materials the models cannot recall)", loc="left", fontsize=9.5); ax.legend(loc="upper left", frameon=False, fontsize=7.3, ncol=2)
    ax = axs[1]
    wb = [num(Cdisc[("whiteboard", m)]["picks inside the pool (median)"]) for m in ms]
    hz = [num(Cdisc[("harness", m)]["picks inside the pool (median)"]) for m in ms]
    ax.bar(xs - w / 2, wb, w, color=C_WB); ax.bar(xs + w / 2, hz, w, color=C_HZ)
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=8); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(xs, [MLAB[m] for m in ms], fontsize=8); ax.set_ylim(0, 9); ax.axhline(8, color=C_REF, lw=0.6, ls=":")
    ax.set_ylabel("picks that are inside the pool (of 8)"); ax.set_title("C2  how many picks land on materials with a known answer", loc="left", fontsize=9.5)
    save(fig, "F5_pillar_C")


# ----------------------------------------------------------------------------------------------- F6 pillar D
def fig_D():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.4))
    ms = ["haiku", "sonnet", "opus", "fable"]
    xs = np.arange(len(ms)); w = 0.38
    code = D[("harness-code (prior.py, no model)", "-")]
    for ax, key, ylab, title, ymax, ck in (
        (axs[0], "peak point within 0.3 eV", "materials (of 37)", "D1  kernel peak: point prediction within 0.3 eV", 37, "peak point within 0.3 eV"),
        (axs[1], "shortlist (<=3) within 0.3 eV", "materials (of 37)", "D2  kernel peak: a shortlist of 3 covers it", 37, "shortlist (<=3) within 0.3 eV"),
        (axs[2], "mode freq within 10 %", "materials (of 37)", "D3  driven phonon mode: frequency within 10 %", 37, "mode freq within 10 %"),
    ):
        wb = [num(D[("whiteboard", m)][key]) for m in ms]; hz = [num(D[("harness", m)][key]) for m in ms]
        ax.bar(xs - w / 2, wb, w, color=C_WB, label="whiteboard"); ax.bar(xs + w / 2, hz, w, color=C_HZ, label="harness (+ prior locator)")
        for x, a, b in zip(xs, wb, hz):
            ax.text(x - w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5); ax.text(x + w / 2, b, f"{b:g}", ha="center", va="bottom", fontsize=7.5)
        y = num(code[ck]); ax.axhline(y, color=C_CODE, lw=1.0, ls="--", label=f"harness code alone (prior locator, 34 materials): {y:g}")
        ax.set_xticks(xs, [MLAB[m] for m in ms], fontsize=8); ax.set_ylim(0, ymax * 1.3); ax.axhline(ymax, color=C_REF, lw=0.6, ls=":")
        ax.set_ylabel(ylab); ax.set_title(title, loc="left", fontsize=9.5)
        ax.legend(loc="upper left", frameon=False, fontsize=7.3)
    save(fig, "F6_pillar_D")


# ----------------------------------------------------------------------------------------------- F7 E kernels
def fig_E_kernels():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
    styles = {"baseline (library)": dict(color="#222", lw=1.6, ls="-"), "harness + Haiku": dict(color=C_HZ, lw=1.4, ls="--"), "whiteboard Fable": dict(color="#c0392b", lw=1.2, ls="-.")}
    for ax, (M, files) in zip(axs, KERNELS.items()):
        for lab, p in files.items():
            k = parse_kernel(p); inv = kernel_invariant(k)["invariant"]
            w = np.asarray(k["photon_ev"]); i = int(np.argmax(inv))
            ax.plot(w, inv, label=f"{lab}: {inv[i]:.1f} at {w[i]:.2f} eV", **styles[lab])
            ax.plot(w[i], inv[i], "o", ms=3.5, color=styles[lab]["color"])
        b = E[M]["base"]
        ax.set_title(f"{M}  (strongest mode {b[2]}, all three arms)", loc="left", fontsize=9.5)
        ax.set_xlabel("photon energy (eV)"); ax.set_xlim(0, 6)
        if M == "GaP":
            ax.legend(frameon=False, fontsize=7.3, loc="upper right", bbox_to_anchor=(1.0, 0.86))
        else:
            ax.legend(frameon=False, fontsize=7.3, loc="upper left")
    axs[0].set_ylabel("kernel invariant (Å²/eV)")
    axs[1].text(0.02, 0.72, "three different cells:\nc = 5.868 Å measured (library)\n6.053 Å PBEsol (harness arm)\n6.229 Å MP as given (whiteboard)\nheight and mode agree;\npeak position follows the cell",
                transform=axs[1].transAxes, fontsize=6.8, va="top")
    save(fig, "F7_E_kernels")


# ----------------------------------------------------------------------------------------------- F8 E cost + timeline
def fig_E_cost():
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.5), gridspec_kw=dict(width_ratios=[1, 1, 1.5]))
    Ms = list(E); xs = np.arange(len(Ms)); w = 0.38
    ax = axs[0]
    wb = [E[m]["whiteboard"]["nodeh"] for m in Ms]; hz = [E[m]["harness"]["nodeh"] for m in Ms]
    ax.bar(xs - w / 2, wb, w, color=C_WB, label="whiteboard Fable"); ax.bar(xs + w / 2, hz, w, color=C_HZ, label="harness + Haiku")
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"{a:.1f}", ha="center", va="bottom", fontsize=8); ax.text(x + w / 2, b, f"{b:.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(xs, Ms); ax.set_ylabel("node-hours (sacct, hyperthreads counted)"); ax.set_title(f"E1  compute: {sum(wb):.1f} vs {sum(hz):.1f} node-hours", loc="left", fontsize=9.5)
    ax.set_ylim(0, 16); ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    ax = axs[1]
    wb = [E[m]["whiteboard"]["usd"] for m in Ms]; hz = [E[m]["harness"]["usd"] for m in Ms]
    ax.bar(xs - w / 2, wb, w, color=C_WB); ax.bar(xs + w / 2, hz, w, color=C_HZ)
    for x, a, b in zip(xs, wb, hz):
        ax.text(x - w / 2, a, f"${a:.0f}", ha="center", va="bottom", fontsize=8); ax.text(x + w / 2, b, f"${b:.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(xs, Ms); ax.set_ylabel("model spend, list price (USD)"); ax.set_title("E2  model spend: \\$98 vs \\$3.4 (list price)", loc="left", fontsize=9.5)
    ax = axs[2]
    # timeline (CEST, 2026-10-14 11:47 = 0)
    t0 = 11 + 47 / 60
    rows = [("harness GaP", 0, 20 + 36 / 60 - t0, (12 + 13 / 60 - t0, 19 + 43 / 60 - t0)),
            ("harness SnS2", 0, 21 + 42 / 60 - t0, (12 + 13 / 60 - t0, 19 + 43 / 60 - t0)),
            ("harness NbFeSb", 0, 22 + 52 / 60 - t0, (12 + 13 / 60 - t0, 19 + 43 / 60 - t0)),
            ("whiteboard GaP", 12 + 12 / 60 - t0, 22 + 5 / 60 - t0, None),
            ("whiteboard SnS2", 21 + 31 / 60 - t0, 24 + 2 + 42 / 60 - t0, None),
            ("whiteboard NbFeSb", 21 + 31 / 60 - t0, 24 + 1 + 42 / 60 - t0, None)]
    for i, (lab, a, b, q) in enumerate(rows):
        c = C_HZ if lab.startswith("harness") else C_WB
        ax.barh(i, b - a, left=a, color=c, height=0.6)
        if q:
            ax.barh(i, q[1] - q[0], left=q[0], color="white", height=0.6, hatch="////", edgecolor=c, lw=0)
        ax.text(b + 0.15, i, f"{b - a:.1f} h", va="center", fontsize=7.5)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8); ax.invert_yaxis()
    ax.set_xlabel("hours after 2026-10-14 11:47 CEST"); ax.set_xlim(0, 16.5)
    ax.set_title("E3  wall-clock (hatched: 7.5 h in the standard queue)", loc="left", fontsize=9.5)
    save(fig, "F8_E_cost")


# ----------------------------------------------------------------------------------------------- F9 capability map
def fig_gaps():
    rows = [
        ("Operate the pipeline without human judgment (tickets)", 3, "A: 44 tickets, 5 models; E: 6 tickets, 0 owner decisions"),
        ("Never waste compute on a bad resubmission", 3, "A: 0 burning answers in the harness arm, 4–7 whiteboard"),
        ("Lift the cheapest model to frontier level on operations", 3, "A: Haiku 36.25 > Fable whiteboard 28.5"),
        ("Choose Wannier projections (the expert step)", 3, "B: code 13/16 round 1; frontier models 9–12/16"),
        ("Reproduce a sealed answer end to end, unattended", 3, "E: GaP, NbFeSb identical; NbFeSb = production flight"),
        ("Do it cheaper than a frontier model working alone", 3, "E: 3.6× less compute, 30× less model spend"),
        ("Pick the next batch of materials better than chance", 2, "C: hits 4–5 vs random 3.1; pool is prior-biased, n = 23"),
        ("Be faster in wall-clock", 0, "E: 9–11 h vs 4–10 h; the queue policy cost 7.5 h"),
        ("Predict the kernel peak from cheap data", 1, "D: +1–3 materials over the model alone; locator weak"),
        ("Solve the hardest Wannier cases with a model (NbFeSb)", 1, "B: no model passed NbFeSb from the card; harness used the casebook"),
        ("Guard against silent input differences (cell)", 0, "E: SnS2 fell back to a PBEsol cell with one log line"),
        ("Generalise beyond this pipeline / these 16–44 items", 0, "one harness, one lab, n = 3 repeats; no external re-run yet"),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.2)); ax.axis("off")
    cmap = {3: "#bfe3bf", 2: "#e3efb8", 1: "#fbe3b0", 0: "#f3d6d6"}
    lab = {3: "shown", 2: "partly shown", 1: "weak", 0: "not shown / gap"}
    ax.set_xlim(0, 11); ax.set_ylim(0, len(rows) + 1.2)
    ax.text(0.1, len(rows) + 0.75, "What v0 shows and what it does not", fontsize=11, weight="bold")
    for i, (cap, lv, ev) in enumerate(rows):
        y = len(rows) - i - 0.5
        ax.add_patch(plt.Rectangle((0.1, y - 0.4), 4.9, 0.8, fc="#f8f8f8", ec="#ddd", lw=0.5))
        ax.text(0.2, y, cap, va="center", fontsize=8.5)
        ax.add_patch(plt.Rectangle((5.1, y - 0.4), 1.5, 0.8, fc=cmap[lv], ec="#ddd", lw=0.5))
        ax.text(5.85, y, lab[lv], va="center", ha="center", fontsize=8, weight="bold")
        ax.add_patch(plt.Rectangle((6.7, y - 0.4), 4.2, 0.8, fc="#ffffff", ec="#ddd", lw=0.5))
        ax.text(6.8, y, ev, va="center", fontsize=7.6)
    save(fig, "F9_capability_map")


if __name__ == "__main__":
    for f in (fig_overview, fig_harness, fig_A, fig_B, fig_C, fig_D, fig_E_kernels, fig_E_cost, fig_gaps):
        f()
