#!/usr/bin/env python3
"""Compare the current MoS2 mode-8 kernel with Trovatello et al. Fig. 7b.

Only spectral shape is compared.  The experiment reports optical-modulation
amplitude, whereas the calculation reports a coherent-phonon generation kernel.
The fitted vertical scale therefore has no physical meaning.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


CHANNELS = ["xx", "yy", "zz", "xy", "xz", "yz", "yx", "zx", "zy"]
EXPERIMENT_FREQUENCY_CM1 = 406.0
MEV_TO_CM1 = 8.06554394


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fortran_float(token: str) -> float:
    """Accept ordinary floats and EPW's exponent-without-E form."""
    try:
        return float(token)
    except ValueError:
        match = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))([+-]\d{2,3})", token)
        if match is None:
            raise
        return float(f"{match.group(1)}e{match.group(2)}")


def read_mode(path: Path, wanted_mode: int) -> tuple[float, np.ndarray, np.ndarray]:
    rows: list[list[float]] = []
    active = False
    phonon_mev = None
    for line in path.read_text().splitlines():
        words = line.split()
        if not words or words[0] == "#":
            continue
        if words[0] == "imode":
            mode = int(words[2])
            if active and mode != wanted_mode:
                break
            active = mode == wanted_mode
            if active:
                phonon_mev = float(words[3])
        elif active:
            rows.append([fortran_float(item) for item in words])
    if phonon_mev is None or not rows:
        raise ValueError(f"mode {wanted_mode} not found in {path}")
    raw = np.asarray(rows, dtype=float)
    if raw.shape[1] != 1 + 2 * len(CHANNELS):
        raise ValueError(f"expected 9 complex channels; got {raw.shape[1] - 1} values per row")
    energy = raw[:, 0]
    gamma = raw[:, 1::2] + 1j * raw[:, 2::2]
    return phonon_mev, energy, gamma


def read_experiment(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
    return tuple(
        np.asarray([float(row[name]) for row in rows], dtype=float)
        for name in (
            "pump_energy_ev",
            "oscillation_amplitude_x1e_minus4",
            "digitization_energy_uncertainty_ev",
            "digitization_amplitude_uncertainty_x1e_minus4",
        )
    )


def gaussian_average_complex(
    energy: np.ndarray, signal: np.ndarray, intensity_fwhm_ev: float
) -> np.ndarray:
    """Average complex Gamma over an illustrative Gaussian pump-intensity spectrum."""
    if intensity_fwhm_ev <= 0:
        return signal.copy()
    spacing = float(np.median(np.diff(energy)))
    sigma = intensity_fwhm_ev / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    half_width = int(np.ceil(5.0 * sigma / spacing))
    offsets = np.arange(-half_width, half_width + 1) * spacing
    weights = np.exp(-0.5 * (offsets / sigma) ** 2)
    weights /= np.sum(weights)
    return np.convolve(signal.real, weights, mode="same") + 1j * np.convolve(
        signal.imag, weights, mode="same"
    )


def shape_metrics(
    energy: np.ndarray, curve: np.ndarray, exp_energy: np.ndarray, exp_amplitude: np.ndarray
) -> tuple[dict[str, float], np.ndarray]:
    sampled = np.interp(exp_energy, energy, curve)
    denominator = float(np.dot(sampled, sampled))
    scale = float(np.dot(sampled, exp_amplitude) / denominator)
    predicted = scale * sampled
    return (
        {
            "least_squares_vertical_scale": scale,
            "pearson_at_7_points": float(np.corrcoef(predicted, exp_amplitude)[0, 1]),
            "relative_l2_after_vertical_scale": float(
                np.linalg.norm(predicted - exp_amplitude) / np.linalg.norm(exp_amplitude)
            ),
        },
        predicted,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gamma", type=Path, help="Current Gamma_alphabeta_s.dat")
    parser.add_argument(
        "--experiment",
        type=Path,
        default=Path(__file__).with_name("fig7b_digitized.csv"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--mode", type=int, default=8)
    parser.add_argument(
        "--illustrative-pump-fwhm-ev",
        type=float,
        default=0.10,
        help="Gaussian pump-intensity bandwidth; illustrative because the paper gives only <20 fs",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    phonon_mev, energy, gamma = read_mode(args.gamma, args.mode)
    exp_energy, exp_amplitude, exp_xerr, exp_yerr = read_experiment(args.experiment)

    # The A1' mode is isotropic in-plane.  Average the complex xx and yy amplitudes
    # before taking the magnitude, as required for a finite-bandwidth coherent drive.
    in_plane_gamma = 0.5 * (
        gamma[:, CHANNELS.index("xx")] + gamma[:, CHANNELS.index("yy")]
    )
    raw_curve = np.abs(in_plane_gamma)
    averaged_gamma = gaussian_average_complex(
        energy, in_plane_gamma, args.illustrative_pump_fwhm_ev
    )
    bandwidth_curve = np.abs(averaged_gamma)

    raw_metrics, raw_prediction = shape_metrics(
        energy, raw_curve, exp_energy, exp_amplitude
    )
    bandwidth_metrics, bandwidth_prediction = shape_metrics(
        energy, bandwidth_curve, exp_energy, exp_amplitude
    )

    window = (energy >= 1.8) & (energy <= 4.5)
    raw_peak_index = np.argmax(raw_curve[window])
    calc_peak_ev = float(energy[window][raw_peak_index])
    exp_largest_index = int(np.argmax(exp_amplitude))
    exp_largest_ev = float(exp_energy[exp_largest_index])
    calc_frequency_cm1 = float(phonon_mev * MEV_TO_CM1)

    metrics = {
        "status": "partial_match_not_validation",
        "comparison_scope": (
            "Normalized pump-energy shape only; no absolute displacement comparison, "
            "no pump-by-pump fluence correction, and no energy-axis shift."
        ),
        "calculation": {
            "source": str(args.gamma.resolve()),
            "sha256": sha256(args.gamma),
            "mode": args.mode,
            "mode_energy_mev": float(phonon_mev),
            "mode_frequency_cm-1": calc_frequency_cm1,
            "main_peak_1p8_to_4p5_ev": calc_peak_ev,
            "kernel_part": "Gamma_c only",
            "polarization_curve": "complex average of xx and yy",
        },
        "experiment": {
            "source": "Trovatello et al., ACS Nano 14, 5700-5710 (2020), Fig. 7b",
            "doi": "10.1021/acsnano.0c00309",
            "digitized_csv": str(args.experiment.resolve()),
            "sha256": sha256(args.experiment),
            "number_of_points": int(len(exp_energy)),
            "mode_frequency_cm-1": EXPERIMENT_FREQUENCY_CM1,
            "largest_measured_point_ev": exp_largest_ev,
            "observable": "Fourier amplitude of optical modulation at a fixed 2.9 eV probe",
        },
        "direct_differences": {
            "mode_frequency_calculation_minus_experiment_cm-1": float(
                calc_frequency_cm1 - EXPERIMENT_FREQUENCY_CM1
            ),
            "mode_frequency_relative_percent": float(
                100.0 * (calc_frequency_cm1 - EXPERIMENT_FREQUENCY_CM1)
                / EXPERIMENT_FREQUENCY_CM1
            ),
            "calculation_peak_minus_largest_measured_point_ev": float(
                calc_peak_ev - exp_largest_ev
            ),
        },
        "unbroadened_shape": raw_metrics,
        "illustrative_finite_pump_shape": {
            "gaussian_intensity_fwhm_ev": args.illustrative_pump_fwhm_ev,
            "warning": "Illustrative only: the paper reports <20 fs pulses, not each pulse spectrum.",
            **bandwidth_metrics,
        },
        "known_model_mismatches": [
            "The experiment has strong excitons (bound electron-hole pairs); the present EPW kernel does not include them explicitly.",
            "The experiment adjusted incident fluence with pump energy but did not publish the per-energy values.",
            "The present calculation is no-SOC and Gamma_c only.",
            "The experiment measures optical modulation, not an atom displacement in angstrom.",
        ],
    }

    metrics_path = args.output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n")

    experiment_norm = exp_amplitude / np.max(exp_amplitude)
    raw_norm = raw_curve / np.max(raw_curve[window])
    bandwidth_norm = bandwidth_curve / np.max(bandwidth_curve[window])

    fig, axes = plt.subplots(2, 1, figsize=(9.0, 9.0), sharex=True)
    ax = axes[0]
    ax.errorbar(
        exp_energy,
        experiment_norm,
        xerr=exp_xerr,
        yerr=exp_yerr / np.max(exp_amplitude),
        fmt="o",
        color="#111111",
        capsize=2,
        label="experiment: 7 digitized points",
    )
    ax.plot(energy, raw_norm, color="#0072B2", linewidth=2.0, label="calculation: narrow-band")
    ax.plot(
        energy,
        bandwidth_norm,
        color="#D55E00",
        linewidth=1.8,
        linestyle="--",
        label=f"calculation: illustrative {args.illustrative_pump_fwhm_ev:.2f} eV pump bandwidth",
    )
    ax.axvline(exp_largest_ev, color="#111111", alpha=0.25, linewidth=1.0)
    ax.axvline(calc_peak_ev, color="#0072B2", alpha=0.30, linewidth=1.0)
    ax.set_ylabel("amplitude, each curve normalized")
    ax.set_title("Monolayer MoS$_2$: measured A$_1'$ generation profile vs current mode-8 kernel")
    ax.grid(alpha=0.18)
    ax.legend(fontsize=9)

    ax = axes[1]
    ax.errorbar(
        exp_energy,
        exp_amplitude,
        xerr=exp_xerr,
        yerr=exp_yerr,
        fmt="o",
        color="#111111",
        capsize=2,
        label="experiment",
    )
    ax.plot(
        exp_energy,
        raw_prediction,
        "s-",
        color="#0072B2",
        label=(
            "calculation at the same 7 energies "
            f"(r={raw_metrics['pearson_at_7_points']:.2f})"
        ),
    )
    ax.plot(
        exp_energy,
        bandwidth_prediction,
        "^--",
        color="#D55E00",
        label=(
            f"illustrative finite pump (r={bandwidth_metrics['pearson_at_7_points']:.2f})"
        ),
    )
    ax.set_xlabel("pump photon energy (eV)")
    ax.set_ylabel(r"optical-oscillation amplitude ($10^{-4}$)")
    ax.set_xlim(1.8, 4.5)
    ax.grid(alpha=0.18)
    ax.legend(fontsize=9)
    ax.text(
        0.015,
        0.03,
        "Vertical scale fitted; no energy shift and no per-energy fluence correction.\n"
        "Digitized error bars show figure-reading uncertainty only.",
        transform=ax.transAxes,
        fontsize=8.5,
        va="bottom",
    )

    fig.tight_layout()
    fig.savefig(args.output_dir / "mos2_experiment_vs_current.png", dpi=200)
    plt.close(fig)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
