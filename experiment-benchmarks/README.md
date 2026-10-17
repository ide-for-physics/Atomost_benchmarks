# Experiment benchmarks: calibrating the coherent-phonon theory against published experiments (round 1)

These folders check the physics our pipeline computes against published measurements. For every phonon mode *s* of a crystal the
pipeline computes, from first principles, a generation kernel Γ_s^ab(E): how strongly a light pump of photon energy E and
polarisations a, b drives that mode coherently. The kernel describes resonant driving above the direct band gap (resonant stimulated
Raman scattering) and is zero below the gap by construction.

The benchmark asks one question: **given the same material and the same pump conditions as an experiment, does the theory predict
what the experiment measured?** It is one turn of a loop: we compute, we compare with experiments, and we state new predictions for
experiments that have not been done yet. Round 1 (2026-08-31 to 2026-10-11) compared the theory with published third-party
experiments; it ends with predictions on record that are waiting for a measurement.

## Results of round 1

| What was compared | Experiment | Result |
|---|---|---|
| NbOI₂ (bulk): which mode an above-gap pump drives, and the axis it radiates along | Huang et al. 2025 (pump–probe, 2.58 eV, ~150 fs; THz transmission); Subedi et al. 2025 (THz emission) | **match**: the ferroelectric transverse-optical mode, and the polar *b* axis, with no adjustable parameter |
| MoS₂ (monolayer): where the driving peaks against the pump photon energy, and the rise to the peak | Trovatello et al. 2020 (pump scanned 2.0–4.3 eV) | **match**: computed peak 2.83 eV, largest measured response 2.95 eV; the rise from 2.07 to 2.95 eV follows the measurement |
| InP (bulk): where the driving resonates | Aspnes & Studna 1983 (ellipsometry); Mooradian & Wright 1966 (Raman) | **match**: main resonance on the measured E₁ transition (3.21 vs 3.20 eV) |
| Relative strength between materials | the crystals known experimentally as strong THz materials | the ranking puts KNbO₃, BaTiO₃ and LiNbO₃ first, about 6–11 times above GaP and InP |

All comparisons were made after the experiments were published. Not anchored by any experiment yet: the absolute amplitude (the
displacement per unit field, or the emitted THz field) of any material.

## NbOI₂

Huang et al. pumped above the 2.30 eV direct gap (2.58 eV, ~150 fs) and saw a single coherent oscillation at 3.125 THz; their THz
transmission shows a strong absorption at 3.13 THz along the polar *b* axis and a weak one at 1.78 THz. We evaluated the kernel at
that pump energy, after one rigid shift of the photon axis equal to the measured direct gap minus the computed (PBE) gap of the same
cell (2.30 − 0.825 = 1.475 eV), and weighted each mode by the factor with which a 150 fs Gaussian pulse can drive a mode of that
frequency. The ferroelectric transverse-optical mode, 2.83 THz in our calculation (about 10 % below the measured 3.13 THz, the usual
PBE softening of a ferroelectric mode, the same in the authors' own calculation), then carries 69 % of the driving; the 1.78 THz mode
is second with 13 %. A kernel that is flat in photon energy, with the same pulse factor, would pick the lowest mode (1.61 THz)
instead, so the selection comes from the kernel. The driven mode's dipole lies along *b*; the measured absorption at 3.1 THz is
about three times stronger along *b* than along *c*, and the field emitted in Subedi et al. is polarised along *b* (E_b ≈ 6 E_c).

The comparison uses the measured lattice (Rijnsdorp and Jellinek 1978), which the pipeline prefers. An earlier calculation ran on a
relaxed cell, the pipeline's fallback when its search for a measured lattice came back empty; that cell halves the Nb off-centring
(0.053 vs 0.130 Å) and put the polar character on the wrong modes (1.7–1.95 THz), in disagreement with the measured THz spectrum. On
the measured lattice the polar mode set matches the measurement: transverse 2.83 THz with its longitudinal partner at 3.10 THz
(measured absorption 3.13 THz; the authors' calculation 2.830 → 3.128 THz). Figures 3–6 of the calibration report show these steps.

## MoS₂ (monolayer)

Trovatello et al. pumped at seven photon energies from 2.0 to 4.3 eV (pulses shorter than 20 fs), probed at 2.9 eV and report the
oscillation amplitude of the out-of-plane A₁′ mode (~406 cm⁻¹) at each pump energy (their Fig. 7b); we read the seven points from
the vector figure of the paper's arXiv source. Our A₁′ mode lies at 396.7 cm⁻¹ (−2.3 %). The comparison tests a pump scheme, so it
is judged by where the driving peaks and whether the points near the peak follow the computed trend:

- the computed driving peaks at 2.83 eV with no energy shift; the largest measured point is at 2.95 eV, within the spacing of the
  measured points;
- over the six points from 2.07 to 2.95 eV the measured rise follows the computed one: Pearson correlation 0.65, or 0.82 with an
  illustrative 0.10 eV pump bandwidth (the paper gives only the pulse length).

Away from the peak, at 4.27 eV, the calculation gives strong driving where the measurement is weak (0.28 of its maximum); this is the
high-energy region, far from the pump scheme, where excitons and spin–orbit coupling, absent from our calculation, matter most. The
2026-08-31 report labels the comparison a partial match on an all-point correlation (0.43, pulled down mainly by the 4.27 eV point);
`2026-10-17_MoS2_peak_trend/` holds the peak-and-rise evaluation and its numbers. Other limits: the experiment measures optical
modulation at a fixed probe, not atomic displacement, and does not publish the fluence at each pump energy.

## InP (bulk)

No published experiment scans the pump photon energy of a coherent phonon in bulk InP, so the check is on positions. With one rigid
shift of the photon axis equal to the computed gap error (1.344 − 0.446 = 0.898 eV), the kernel's main resonance lies at 3.21 eV, on
the measured E₁ critical point at 3.20 eV (the ε₂ peak in Aspnes & Studna's data); E₁ and the fundamental gap are independent
quantities, so this is not a consequence of the shift. The second resonance lies at 5.10 eV against the ε₂ maximum of the E₀′/E₂
complex at 4.70 eV. The computed Γ optical phonon is 284.9 cm⁻¹ against 303.7 cm⁻¹ for the measured Raman TO (−6 %). The only
time-domain coherent-TO measurement we located (Mante et al. 2020, nanowires, one pump energy) finds the TO amplitude independent of
doping, consistent with the second-order generation the kernel describes.

## Relative strength

The screening score of the public materials explorer ([cophon.insights4all.org](https://cophon.insights4all.org), score version 2.1,
unit = InP under its best commercial pulsed source) combines the kernel, each mode's dipole and the commercially available pulsed
sources. It ranks the three crystals known experimentally as strong THz materials first: KNbO₃ 4.71, BaTiO₃ 3.33, LiNbO₃ 3.02; the
common semiconductors GaP and InP score 0.54 and 0.43. The ranking is consistent with what is known experimentally; no experiment yet
compares two materials under the same above-gap pump in one apparatus.

## Predictions on record, not yet tested

- **NbOI₂, 400 nm (3.10 eV) pump with 35 fs pulses:** the 2.83 THz ferroelectric mode still leads (24 % of the pulse-weighted
  driving), with sidebands at 7.9 THz (17 %), 4.2 THz (17 %), 6.2 THz (14 %) and 14.4 THz (11 %). Pumped at the kernel's own
  resonance (~3.8 eV) with 35 fs or shorter, the leading mode changes to the 6.22 THz mode (36 %). The one above-gap emission trace
  that exists (Subedi et al., 400 nm, 30 fs) shows the 2.86 THz line the kernel ranks first; its detection stops at 4 THz, below the
  predicted sidebands. Calibration report Fig. 8 gives the full ladder of five pump conditions.
- **InP, pump tuned to E₁ (3.21 eV):** the TO mode is driven about 4 times more strongly than with the 550 nm pump of Mante et al.,
  at the same fluence (kernel invariant relative to its E₁ peak: 550 nm 0.23, 620 nm 0.26, 400 nm 0.52, E₁ 1.00).

We seek collaborations in ultrafast optical measurement and coherent-phonon experiments to test them.

## Rules used in every comparison

- At most one rigid shift of the photon axis, fixed by the measured gap minus the computed gap of the same cell (NbOI₂ 1.475 eV, InP
  0.898 eV; MoS₂ unshifted). No other parameter is adjusted, except one vertical scale for the normalised MoS₂ curve.
- Pump photon energy and pulse duration are taken from the paper. A mode's driving is the rotational invariant
  |Γ_s| = (Σ_ab |Γ_s^ab|²)^½, or the channel stated in the report; for NbOI₂ the Gaussian pulse factor is
  F(ν, τ) = exp[−(2πντ)² / (16 ln 2)].
- Frequencies, rankings, resonance positions and normalised shapes are compared; absolute amplitudes are not.
- Kernel values quoted in Å²/eV in these files (for example 4.76 for the NbOI₂ 2.83 THz mode at the pump energy, or the InP peak of
  14.3) are in the normalisation the kernel files used at the time, the sum over the two photon orderings, which is twice the
  ordering-averaged convention. Every comparison above uses ratios, shares or normalised curves, which this factor does not change.

## The experiments

The papers are cited here and are not redistributed.

Compared:

1. C. Trovatello et al., "Strongly Coupled Coherent Phonons in Single-Layer MoS₂", *ACS Nano* **14**, 5700–5710 (2020).
   doi:[10.1021/acsnano.0c00309](https://doi.org/10.1021/acsnano.0c00309); [arXiv:1912.12744](https://arxiv.org/abs/1912.12744).
2. C.-Y. Huang et al., "Coupling of electronic transition to ferroelectric order in a 2D semiconductor", *Nat. Commun.* **16**, 1896
   (2025). doi:[10.1038/s41467-025-57061-9](https://doi.org/10.1038/s41467-025-57061-9); [arXiv:2410.09238](https://arxiv.org/abs/2410.09238).
3. S. Subedi et al., "Colossal terahertz emission with ultrafast tunability based on van der Waals ferroelectric NbOI₂",
   [arXiv:2412.08058](https://arxiv.org/abs/2412.08058); published in *Adv. Opt. Mater.* (2025).
4. D. E. Aspnes and A. A. Studna, "Dielectric functions and optical parameters of Si, Ge, GaP, GaAs, GaSb, InP, InAs, and InSb from
   1.5 to 6.0 eV", *Phys. Rev. B* **27**, 985–1009 (1983). doi:[10.1103/PhysRevB.27.985](https://doi.org/10.1103/PhysRevB.27.985).
   Tabulated n, k taken from the refractiveindex.info database (public domain, CC0).
5. A. Mooradian and G. B. Wright, *Solid State Commun.* **4**, 431 (1966) (InP Raman TO and LO frequencies).
6. P.-A. Mante et al., "Ultrafast Optical Generation of Coherent Bright and Dark Surface Phonon Polaritons in Nanowires",
   *ACS Photonics* **7**, 1923–1931 (2020). doi:[10.1021/acsphotonics.0c00537](https://doi.org/10.1021/acsphotonics.0c00537);
   [arXiv:1909.02238](https://arxiv.org/abs/1909.02238).
7. I. Vurgaftman, J. R. Meyer and L. R. Ram-Mohan, "Band parameters for III–V compound semiconductors and their alloys",
   *J. Appl. Phys.* **89**, 5815–5875 (2001). doi:[10.1063/1.1368156](https://doi.org/10.1063/1.1368156) (InP gap, used for the shift).

Read for scope, not compared (pumped below the gap, where the kernel is zero; or a surface-field mechanism the kernel does not describe):

8. T. Handa et al., "Terahertz emission from giant optical rectification in a van der Waals material", *Nat. Mater.* **24**,
   1203–1208 (2025). doi:[10.1038/s41563-025-02201-1](https://doi.org/10.1038/s41563-025-02201-1).
9. C.-Y. Huang, T. Handa et al., "Tunable Narrowband Terahertz Radiation from van der Waals Ferroelectrics",
   [arXiv:2512.06139](https://arxiv.org/abs/2512.06139) (2025).
10. T. Pfeifer, T. Dekorsy, W. Kütt and H. Kurz, "Generation mechanism for coherent LO phonons in surface-space-charge fields of
    III-V-compounds", *Appl. Phys. A* **55**, 482–488 (1992). doi:[10.1007/BF00348337](https://doi.org/10.1007/BF00348337).

Candidate experiments listed in `2026-08-31/REPORT.md` for later rounds:

11. Y. Huang et al., "Observation of a Novel Lattice Instability in Ultrafast Photoexcited SnSe", *Phys. Rev. X* **12**, 011029
    (2022). doi:[10.1103/PhysRevX.12.011029](https://doi.org/10.1103/PhysRevX.12.011029).
12. P. Fischer et al., "Microscopic mechanism of displacive excitation of coherent phonons in a bulk Rashba semiconductor",
    *Phys. Rev. B* **111**, L081201 (2025). doi:[10.1103/PhysRevB.111.L081201](https://doi.org/10.1103/PhysRevB.111.L081201).
13. L. Hoang et al., "Ultrafast decoupling of polarization and strain in ferroelectric BaTiO₃", *Nat. Commun.* **16**, 7966 (2025).
    doi:[10.1038/s41467-025-63045-6](https://doi.org/10.1038/s41467-025-63045-6).
14. T. Völzer et al., "Having a good vibe: strong coupling to the electronic system creates incoherent and coherent phonons in
    1L-TMDCs", *2D Mater.* **12**, 035012 (2025). doi:[10.1088/2053-1583/addf5a](https://doi.org/10.1088/2053-1583/addf5a);
    data set doi:[10.18453/rosdok_id00004699](https://doi.org/10.18453/rosdok_id00004699) (CC BY 4.0).
15. K. Yee et al., "Coherent Optical Phonon Oscillations in Bulk GaN Excited by Far below the Band Gap Photons",
    *Phys. Rev. Lett.* **88**, 105501 (2002). doi:[10.1103/PhysRevLett.88.105501](https://doi.org/10.1103/PhysRevLett.88.105501).

## Data from papers in this folder

- `2026-08-31/MoS2_Trovatello_2020/fig7b_digitized.csv`: the seven points we read from the vector Fig. 7b in the arXiv source of
  Trovatello et al. 2020. They are not author-supplied data, and the listed uncertainties cover figure reading only. Cite the paper
  when using them.
- `2026-09-05_InP/InP_Aspnes1983_nk.yml`: the Aspnes & Studna n, k table as distributed by the refractiveindex.info database (CC0);
  `inp_aspnes1983_eps.csv` is our conversion to ε₁ and ε₂.
- Figures drawn by our scripts that plot numbers taken from papers (no figure of a paper is reproduced): calibration report Fig. 3a
  (THz transmission of NbOI₂ along *b* and *c*, digitised from Huang et al. 2025, SI Fig. 9), Figs. 4 and 6 (frequencies, optical
  densities and the E_b/E_c ratio quoted by Huang et al. and Subedi et al.), Fig. 7 and `mos2_experiment_vs_current.png` (the seven
  Trovatello points), `inp_experiment_vs_current.png` (the Aspnes & Studna ε₂ and the quoted phonon frequencies).

## How to read the folders

Each dated folder is the comparison as written on its date, unchanged except that local paths were replaced by `<cophon>/` or `~/`;
paths such as `materials/…` or `records/…` refer to the private project tree. The kernel files and phonon data the scripts read are
not published, so the scripts show how each number was computed but do not run from this repository.

| Path | Contents |
|---|---|
| `2026-08-31/REPORT.md`, `SOURCES.md` | the MoS₂ comparison as first written, and a ranked list of candidate experiments; primary sources |
| `2026-08-31/MoS2_Trovatello_2020/` | `README.md`; `compare_current.py`; `fig7b_digitized.csv` (the seven points); `metrics.json`; `mos2_experiment_vs_current.png` |
| `2026-08-31/open_data/README.md` | pointer to the Völzer et al. open data set (not copied) |
| `2026-09-05_InP/` | `REPORT.md`; `SOURCES.md`; `compare_inp.py`; `metrics.json`; `inp_experiment_vs_current.png`; `InP_Aspnes1983_nk.yml`; `inp_aspnes1983_eps.csv` |
| `2026-10_calibration_report/figures/` | Figs. 1–8 of the calibration report of 2026-10-11 (PDF and PNG): 1 the chain from pump to THz field; 2 the NbOI₂ experiments on the photon-energy axis; 3 measured THz transmission and computed dielectric function; 4 per-mode driving at the experiment's conditions; 5 the kernel against a flat-kernel null model; 6 the polar axis; 7 the MoS₂ shape; 8 the prediction ladder |
| `2026-10_calibration_report/data/figure_data.json` | the numbers behind Figs. 2 and 4–8 |
| `2026-10-17_MoS2_peak_trend/` | `peak_trend.py` and `peak_trend.json`: the MoS₂ comparison judged by the peak and the rise to it |
| `SHA256SUMS` | checksums of every file listed above |

Our text, figures and scripts: © Atomost, as for the rest of this repository. The seven digitised points remain the measurements of
Trovatello et al.; the InP optical-constant table is in the public domain.

## 中文

这一组检验的是理论本身：同一个材料、和实验相同的泵浦条件下，我们算出的相干声子生成核能不能预言实验测到的结果。它是"理论计算、对照实验、
再提出新预测"这一轮的第一圈，对照的都是已发表的第三方实验。结果：NbOI₂ 在泵浦探测实验自己的条件下（2.58 eV，约 150 fs），核选出的主导模就是
实验看到的铁电横光学模（我们算 2.83 THz，实验 3.13 THz），辐射方向也沿极性轴 b，没有可调参数；单层 MoS₂ 算出的驱动峰在 2.83 eV，实验响应最大
的点在 2.95 eV，峰前的上升走势和测量一致；InP 的主共振落在实测的 E₁ 跃迁上（3.21 对 3.20 eV）；公开探索器的筛选分把实验上公认的强太赫兹晶体
KNbO₃、BaTiO₃、LiNbO₃ 排在最前，约为 GaP、InP 的 6 到 11 倍。新的预测已经写下、等待实验检验：NbOI₂ 用 400 nm、35 fs 泵浦时 2.83 THz 模仍居首并出现
4 到 14 THz 的边带；InP 泵浦调到 E₁ 时 TO 模的驱动约为 550 nm 泵浦的 4 倍。绝对幅度目前还没有实验能锚定。论文原文不随仓库发布，只给引用。
