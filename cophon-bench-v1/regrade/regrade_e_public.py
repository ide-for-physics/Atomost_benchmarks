#!/usr/bin/env python3
"""cophon-bench pillar E — re-grade an end-to-end deliverable from PUBLIC files only (no pipeline code needed; numpy only).

    python3 regrade_e_public.py E_baselines.json <material> <Gamma_alphabeta_s.dat> [RESULT.json]

It re-implements the grader's analysis of the kernel file written by the authors' EPW variant (`Gamma_alphabeta_s.dat`: one block per
optical mode, header `imode ... <label> <phonon meV>`, rows = photon energy + 9 complex tensor channels), computes the rotational
invariant sqrt(sum over modes and channels of |Gamma|^2) on the photon grid, finds its top-2 peaks (second peak kept only if >= 50 % of
the first and >= 0.3 eV away), the strongest degenerate mode group (modes within 0.05 meV) at each peak, and applies the v1 rule:
same answer = the arm's top peak within 0.15 eV of one of the baseline's top-2 peaks AND height within 25 % of that peak AND the mode
group's frequency within 5 %. The published E_baselines.json carries the baselines' peaks; the pipeline's own grader
(benchmarks/cophon_bench/pillar_e.py, private) gave identical numbers on the v0 whiteboard deliverables (checked 2026-10-15).
"""
import json, math, re, sys
import numpy as np

TOL_POS_EV, TOL_HEIGHT, TOL_MODE = 0.15, 0.25, 0.05
PEAK_FLOOR, PEAK_MIN_SEP_EV = 0.5, 0.3
MEV_TO_THZ = 0.241798935   # the grader's constant


def ffloat(s: str) -> float:
    return float(re.sub(r"[dD]", "e", s))


def parse_kernel(path: str) -> dict:
    labels, phonon_mev, blocks, rows = [], [], [], []
    for line in open(path, encoding="utf-8", errors="replace"):
        w = line.split()
        if not w or w[0] == "#":
            continue
        if w[0] == "imode":
            if rows:
                blocks.append(np.asarray(rows, float)); rows = []
            labels.append(int(w[2])); phonon_mev.append(float(w[3]))
        else:
            rows.append([ffloat(v) for v in w])
    if rows:
        blocks.append(np.asarray(rows, float))
    raw = np.stack(blocks)
    photon = raw[0, :, 0]
    gamma = raw[:, :, 1::2] + 1j * raw[:, :, 2::2]
    assert gamma.shape[2] == 9, gamma.shape
    return {"modes": labels, "phonon_mev": np.asarray(phonon_mev), "photon_ev": photon, "gamma": gamma}


def top_peaks(w, y):
    idx = [i for i in range(1, len(y) - 1) if y[i] >= y[i - 1] and y[i] > y[i + 1]]
    if len(y) > 1 and y[-1] > y[-2]:
        idx.append(len(y) - 1)
    if not idx:
        return [int(np.argmax(y))]
    idx.sort(key=lambda i: -y[i]); out = [idx[0]]
    for i in idx[1:]:
        if y[i] < PEAK_FLOOR * y[idx[0]]:
            break
        if all(abs(w[i] - w[j]) >= PEAK_MIN_SEP_EV for j in out):
            out.append(i)
        if len(out) == 2:
            break
    return out


def analyse(path: str) -> dict:
    k = parse_kernel(path); w = k["photon_ev"]; gabs2 = np.abs(k["gamma"]) ** 2
    y = np.sqrt(gabs2.sum(axis=(0, 2))); per_mode = np.sqrt(gabs2.sum(axis=2)); f = k["phonon_mev"]
    groups = []
    for i in np.argsort(f):
        if groups and abs(f[i] - f[groups[-1][0]]) < 0.05:
            groups[-1].append(int(i))
        else:
            groups.append([int(i)])
    peaks = []
    for ip in top_peaks(w, y):
        strengths = [math.sqrt(float((per_mode[g, ip] ** 2).sum())) for g in groups]
        gi = int(np.argmax(strengths)); g = groups[gi]
        peaks.append({"photon_ev": round(float(w[ip]), 4), "invariant_a2_per_ev": round(float(y[ip]), 4),
                      "mode_group": {"modes": [k["modes"][i] for i in g], "phonon_mev": round(float(f[g].mean()), 4),
                                     "thz": round(float(f[g].mean()) * MEV_TO_THZ, 4), "share_of_invariant": round(strengths[gi] / max(float(y[ip]), 1e-300), 4)}})
    return {"peaks": peaks, "n_modes": int(len(f)), "photon_grid": {"min_ev": float(w[0]), "max_ev": float(w[-1]), "count": int(len(w))}}


def rel(a, b):
    return (a - b) / b if b else None


def grade(baseline: dict, dat: str, result: dict | None) -> dict:
    an = analyse(dat); bpeaks = baseline["peaks"]; ap = an["peaks"][0]
    matched = next((k for k, bp in enumerate(bpeaks) if abs(ap["photon_ev"] - bp["photon_ev"]) <= TOL_POS_EV + 1e-9), None)
    pos_ok = matched is not None; bp = bpeaks[matched] if pos_ok else bpeaks[0]
    h = rel(ap["invariant_a2_per_ev"], bp["invariant_a2_per_ev"]); m = rel(ap["mode_group"]["thz"], bp["mode_group"]["thz"])
    height_ok = pos_ok and h is not None and abs(h) <= TOL_HEIGHT; mode_ok = m is not None and abs(m) <= TOL_MODE
    self_report = None
    if result:
        self_report = {k: result.get(k) for k in ("peak_ev", "peak_a2_per_ev", "mode_thz", "mode_irrep", "mesh", "node_hours", "wall_hours")}
        if isinstance(result.get("peak_ev"), (int, float)):
            self_report["dev_peak_ev"] = round(float(result["peak_ev"]) - ap["photon_ev"], 3)
        if isinstance(result.get("peak_a2_per_ev"), (int, float)):
            self_report["dev_height_rel"] = round(rel(float(result["peak_a2_per_ev"]), ap["invariant_a2_per_ev"]), 4)
    return {"material": baseline["material"], "kernel_file": dat, "arm_peaks": an["peaks"], "baseline_peaks": bpeaks, "matched_baseline_peak": matched,
            "position_ok": pos_ok, "height_rel": (round(h, 4) if h is not None else None), "height_ok": height_ok,
            "mode_rel": (round(m, 4) if m is not None else None), "mode_ok": mode_ok, "same_answer": bool(pos_ok and height_ok and mode_ok),
            "self_report": self_report,
            "verdict": "same answer" if (pos_ok and height_ok and mode_ok) else "differs: " + ", ".join(k for k, ok in (("position", pos_ok), ("height", height_ok), ("mode", mode_ok)) if not ok)}


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    B = json.load(open(sys.argv[1])); mats = B["materials"] if "materials" in B else B
    base = mats[sys.argv[2]]; base.setdefault("material", sys.argv[2])
    res = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
    print(json.dumps(grade(base, sys.argv[3], res), indent=1))
