# Immediate benchmark: monolayer MoS2

This folder turns Fig. 7b of Trovatello *et al.* (2020) into a transparent first
experiment-versus-calculation check.

What is genuinely comparable: the material (one MoS2 layer), the out-of-plane `A1'`
vibration, and the *shape* of its generation strength as pump photon energy is changed.

What is not comparable yet: absolute displacement. The experiment measures how strongly
the probe light is modulated, not how far an atom moves. Its vertical scale is therefore
fitted once to the calculation. The paper also adjusted pump fluence at each energy but
does not publish those individual values, so this first shape comparison cannot correct
for them.

The black points in `fig7b_digitized.csv` were read from the vector figure in the open
arXiv source. They are not author-supplied raw data and the listed uncertainties cover
figure reading only. `Fig7M.eps` is retained so the extraction can be audited.

Run from the coherent-phonon project root:

```bash
python3 reference/experiment_benchmarks/2026-08-31/MoS2_Trovatello_2020/compare_current.py \
  materials/MoS2/run_qe75_k160/Gamma_alphabeta_s.dat \
  --output-dir reference/experiment_benchmarks/2026-08-31/MoS2_Trovatello_2020
```

The 0.10 eV pump bandwidth is only an illustration. The paper states that all pulses were
shorter than 20 fs but does not give the measured spectrum for each pump energy. The
unbroadened curve is the reproducible primary result.
