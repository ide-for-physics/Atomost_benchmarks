#!/usr/bin/env python3
"""MoS2 (monolayer) against Trovatello et al. 2020 Fig. 7b, judged by the peak and the rise to it (2026-10-17).

    python3 peak_trend.py <Gamma_alphabeta_s.dat of MoS2> [--out peak_trend.json]

Owner 2026-10-17: the comparison tests a pump scheme, so what matters is where the driving peaks against the pump photon energy and
whether the measured points near the peak follow the computed trend; an all-point correlation weights every point alike and is not
the metric. Reuses the reader, the experiment table and the Gaussian pump average of ../2026-08-31/MoS2_Trovatello_2020/compare_current.py
(same mode 8 = A1', same in-plane complex average of xx and yy, no energy shift). Reports the computed peak against the largest
measured point, the computed and measured values at the seven pump energies (each normalised to its largest sampled value), the
Pearson correlation over the six points from 2.07 to 2.95 eV (the rise to the peak) and over all seven, unbroadened and with an
illustrative 0.10 eV pump bandwidth (the paper gives only <20 fs pulses).
"""
import argparse, hashlib, importlib.util, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CC = HERE.parent / "2026-08-31" / "MoS2_Trovatello_2020" / "compare_current.py"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gamma", type=Path)
    ap.add_argument("--out", type=Path, default=HERE / "peak_trend.json")
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("compare_current", CC)
    cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
    _, E, G = cc.read_mode(a.gamma, 8)
    ex, ey, _, _ = cc.read_experiment(CC.with_name("fig7b_digitized.csv"))
    ip = 0.5 * (G[:, cc.CHANNELS.index("xx")] + G[:, cc.CHANNELS.index("yy")])
    rise = ex < 3.5
    out = {"experiment": "Trovatello et al., ACS Nano 14, 5700 (2020), Fig. 7b, seven digitised points",
           "kernel_sha256": hashlib.sha256(a.gamma.read_bytes()).hexdigest(), "mode": 8,
           "largest_measured_point_ev": float(ex[np.argmax(ey)]), "curves": {}}
    for label, curve in (("unbroadened", np.abs(ip)), ("pump_fwhm_0.10_ev", np.abs(cc.gaussian_average_complex(E, ip, 0.10)))):
        s = np.interp(ex, E, curve)
        win = (E >= 1.8) & (E <= 4.5)
        out["curves"][label] = {
            "computed_peak_ev_1p8_to_4p5": float(E[win][np.argmax(curve[win])]),
            "points": [{"pump_ev": round(float(e), 3), "measured_norm": round(float(y), 3), "computed_norm": round(float(c), 3)}
                       for e, y, c in zip(ex, ey / ey.max(), s / s.max())],
            "pearson_rise_2p07_to_2p95_ev_6_points": round(float(np.corrcoef(ey[rise], s[rise])[0, 1]), 3),
            "pearson_all_7_points": round(float(np.corrcoef(ey, s)[0, 1]), 3),
        }
    a.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: (v["computed_peak_ev_1p8_to_4p5"], v["pearson_rise_2p07_to_2p95_ev_6_points"], v["pearson_all_7_points"])
                      for k, v in out["curves"].items()}))


if __name__ == "__main__":
    main()
