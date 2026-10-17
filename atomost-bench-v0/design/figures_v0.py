#!/usr/bin/env python3
"""atomost-bench v0 figures, drawn only from the frozen tables and replay results.

    python3 figures_v0.py

Colours: the dataviz reference categorical slots 1-3 in fixed order (validated all-pairs, light mode):
atomost = slot 1 blue, native = slot 2 orange, none = slot 3 aqua. Every bar carries a direct label.
"""
from __future__ import annotations
import json
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
V = HERE.parent / "atomost-bench-v0"
OUT = V / "report" / "figures"
ARMS = ("none", "native", "atomost")
LABEL = {"none": "no memory", "native": "native (before atomost)", "atomost": "atomost home"}
COL = {"atomost": "#2a78d6", "native": "#eb6834", "none": "#1baf7a"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e2dc", "#fcfcfb"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False})


def bars(ax, groups, series, values, fmt="{:.1f}", ymax=None, title="", ylabel="", fs=8.5):
    """grouped bars: groups on x, one bar per series; values[g][s]; 2 px gaps between bars"""
    n = len(series)
    w = 0.8 / n
    for j, s in enumerate(series):
        xs = [i + (j - (n - 1) / 2) * w for i in range(len(groups))]
        ys = [values[g].get(s) for g in groups]
        ax.bar([x for x, y in zip(xs, ys) if y is not None], [y for y in ys if y is not None], width=w * 0.94,
               color=COL[s], label=LABEL[s], edgecolor=SURF, linewidth=1)
        for x, y in zip(xs, ys):
            if y is not None:
                ax.text(x, y, fmt.format(y), ha="center", va="bottom", fontsize=fs, color=INK)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    if ymax:
        ax.set_ylim(0, ymax)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK)
    ax.set_ylabel(ylabel)


def fig_t1():
    rows = json.loads((V / "tables" / "t1_detail.json").read_text())
    models = [m for m in ("haiku", "opus") if any(r["model"] == m for r in rows)]
    projects = ["cophon", "deeph", "new-tech-tests"]

    def acc(sel):
        return 100 * sum(r["correct"] for r in sel) / len(sel) if sel else None

    fig, axes = plt.subplots(1, 4, figsize=(15, 3.9), gridspec_kw={"width_ratios": [1.3, 1, 1, 1]})
    vals = {m.capitalize(): {a: acc([r for r in rows if r["model"] == m and r["arm"] == a]) for a in ARMS} for m in models}
    bars(axes[0], list(vals), ARMS, vals, fmt="{:.0f}%", ymax=105, title="All 43 items: answered as the team decided", ylabel="% correct")
    for ax, p in zip(axes[1:], projects):
        n = len({r["item"] for r in rows if r["project"] == p})
        v = {m.capitalize(): {a: acc([r for r in rows if r["model"] == m and r["arm"] == a and r["project"] == p]) for a in ARMS} for m in models}
        bars(ax, list(v), ARMS, v, fmt="{:.0f}", ymax=105, title=f"{p} ({n} items)", fs=7.5)
    axes[0].legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.12), ncol=3, fontsize=9)
    fig.suptitle("Task 1 - a fresh session started in the project folder; only the injected memory differs (3 runs each)", x=0.01, ha="left",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "F1_t1_accuracy.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(15, 3.8))
    mean = lambda sel, k: st.mean([r[k] or 0 for r in sel]) if sel else None
    med = lambda sel, k: st.median([r[k] or 0 for r in sel]) if sel else None
    panels = [("ctx0", med, lambda r: True, "Context at start, k tokens (median)", "{:.1f}"),
              ("tokens", mean, lambda r: True, "k tokens per answer (mean, 43 items)", "{:.1f}"),
              ("seconds", mean, lambda r: True, "Seconds per answer (mean)", "{:.1f}"),
              ("tokens", mean, lambda r: r["project"] == "deeph", "deeph only, k tokens (mean)", "{:.1f}")]
    for ax, (k, fn, flt, title, fmt) in zip(axes, panels):
        div = 1 if k == "seconds" else 1000
        v = {m.capitalize(): {a: fn([r for r in rows if r["model"] == m and r["arm"] == a and flt(r)], k) / div for a in ARMS} for m in models}
        bars(ax, list(v), ARMS, v, fmt=fmt, title=title, fs=8)
    axes[0].legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.1), ncol=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "F2_t1_cost.png", dpi=180)
    plt.close(fig)


def fig_t2():
    t = json.loads((V / "results" / "t2" / "policies.json").read_text())["totals"]
    order = [("P1", "a full round every hour"), ("P2", "a round at every hour with significant change"),
             ("P4", "always-on session, one short look per hour"), ("P3", "one fixed round per day"),
             ("P0", "atomost: model-free hourly check, wake on change, <=1/day")]
    fig, ax = plt.subplots(figsize=(12.5, 3.6))
    for i, (k, lab) in enumerate(order):
        d = t[k]
        c = COL["atomost"] if k == "P0" else "#b9b7b0"
        ax.barh(i, d["usd_median"], color=c, height=0.62, edgecolor=SURF)
        if d["hi"] != d["lo"]:
            ax.plot([d["lo"], d["hi"]], [i, i], color=INK2, linewidth=1.2)
        lat = d["latency_h"]["median"]
        tag = "actual" if k == "P0" else "simulated"
        ax.text(max(d["hi"], d["usd_median"]) + 25, i, f"${d['usd_median']:,.0f}  ·  {d['auto_rounds']} rounds  ·  wait to handle: median {lat:.1f} h  ({tag})",
                va="center", fontsize=8.5, color=INK)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([lab for _, lab in order], fontsize=9)
    ax.set_xlim(0, 4400)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel("USD over 10 days (list price; whiskers = quartile range of the per-round cost)")
    ax.set_title("Task 2 - strategist wake policies replayed on the same hourly checks (5 projects, 10-07 to 10-17)",
                 loc="left", fontsize=10.5, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "F3_t2_wake_policies.png", dpi=180)
    plt.close(fig)


def fig_routing():
    """Measured 2026-10-17 from every transcript since 09-17 (records/2026-10-17/atomost-measure/context/report_routing_summary.txt):
    which memory folder each main session actually loaded. Strategist homes count as project homes."""
    periods = [("before atomost\n09-17 to 10-05 (68 sessions)", [0, 36, 11, 17, 4]),
               ("atomost, homes for 2 projects\n10-06 to 10-13 (77)", [25, 26, 13, 3, 10]),
               ("every project has a home\n10-14 to 10-17 (42)", [32, 1, 7, 2, 0])]
    cats = ["the project's own memory home", "shared home-directory ledger (all projects mixed)", "the start folder's own bucket",
            "another folder's bucket", "not recorded / test probe"]
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
    fig, ax = plt.subplots(figsize=(12.5, 3.4))
    for i, (lab, vals) in enumerate(periods):
        tot, left = sum(vals), 0.0
        for c, v, col in zip(cats, vals, cols):
            w = 100 * v / tot
            if w:
                ax.barh(i, w, left=left, color=col, edgecolor=SURF, linewidth=2, height=0.6, label=c if i == 0 or (i == 1 and c == cats[0]) else None)
                if w >= 6:
                    ax.text(left + w / 2, i, f"{v}", ha="center", va="center", fontsize=9, color="#ffffff" if col in ("#2a78d6", "#eb6834") else INK)
            left += w
    ax.set_yticks(range(len(periods)))
    ax.set_yticklabels([p for p, _ in periods], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of main sessions (numbers inside = sessions)")
    h, l = ax.get_legend_handles_labels()
    order = [l.index(c) for c in cats if c in l]
    ax.legend([h[k] for k in order], [l[k] for k in order], frameon=False, loc="upper left", bbox_to_anchor=(0, -0.22), ncol=3, fontsize=8.5)
    ax.set_title("Which memory a session actually loaded (measured from Claude Code's own transcripts)", loc="left", fontsize=10.5, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "F4_memory_routing.png", dpi=180)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (V / "tables" / "t1_detail.json").is_file():
        fig_t1()
    fig_t2()
    fig_routing()
    print("figures in", OUT)


if __name__ == "__main__":
    main()
