#!/usr/bin/env python3
"""Fill scripts/report_template.md -> REPORT.md from the kernel files, jobs.log and RESULT.json.
Usage: write_report.py adopted_mesh  (e.g. 144x144x144); meshes present in kernel/ are detected."""
import sys, json, re, glob, os, numpy as np
adopted = sys.argv[1]
def parse(fn):
    modes = {}; cur = None
    for line in open(fn):
        s = line.split()
        if not s or s[0] == '#': continue
        if s[0] == 'imode': cur = (int(s[2]), float(s[3])); modes[cur] = []; continue
        modes[cur].append([float(x) for x in s])
    ims = sorted(modes); w = np.array(modes[ims[0]])[:, 0]
    G = np.array([np.array(modes[im])[:, 1::2] + 1j*np.array(modes[im])[:, 2::2] for im in ims])
    return ims, w, G
meshes = sorted({int(re.search(r'_(\d+)x', f).group(1)) for f in glob.glob('kernel/Gamma_alphabeta_s_*x*x*.dat')})
rows = []; spectra = {}
for n in meshes:
    ims, w, G = parse(f'kernel/Gamma_alphabeta_s_{n}x{n}x{n}.dat')
    M = np.abs(G).sum(axis=2); sel = (w > 0) & (w <= 6 + 1e-9)
    S = M.sum(axis=0); F = np.sqrt((np.abs(G)**2).sum(axis=(0, 2)))
    k = int(np.argmax(np.where(sel, M, -1).max(axis=0))); s = int(np.argmax(M[:, k]))
    rows.append((n, w[k], M[s, k], ims[s][0], S[k], F[k], M[:, k])); spectra[n] = (w, S, F)
res = json.load(open('RESULT.json'))
tab = "| fine k-mesh | peak photon energy (eV) | max_s M_s (Å²/eV) | mode (imode) | Σ_s M_s over the T2 triplet (Å²/eV) | Frobenius ‖Γ‖ (Å²/eV) | M_4, M_5, M_6 at the peak |\n|---|---|---|---|---|---|---|\n"
for n, wk, mk, im, sk, fk, Ms in rows:
    b = '**' if f'{n}x{n}x{n}' == adopted else ''
    tab += f"| {b}{n}×{n}×{n}{b} | {b}{wk:.2f}{b} | {b}{mk:.3f}{b} | {im} | {sk:.2f} | {fk:.3f} | {', '.join(f'{x:.2f}' for x in Ms)} |\n"
diff = "\nDifferences between consecutive meshes of the triplet-summed spectrum S(ω) = Σ_s M_s(ω) (RMS over 0–6 eV relative to the mean of S; max relative to the peak):\n\n| meshes | RMS ΔS / ⟨S⟩ (0–6 eV) | max ΔS / max S | RMS ΔS / ⟨S⟩ (2.5–3.5 eV) | peak max_s M_s change |\n|---|---|---|---|---|\n"
for (n1, _, m1, *_), (n2, _, m2, *_) in zip(rows, rows[1:]):
    w, S1, _ = spectra[n1]; _, S2, _ = spectra[n2]; sel = (w > 0) & (w <= 6); pk = (w >= 2.5) & (w <= 3.5); d = S2 - S1
    diff += f"| {n1}³ → {n2}³ | {np.sqrt((d[sel]**2).mean())/S2[sel].mean()*100:.1f} % | {np.abs(d[sel]).max()/S2[sel].max()*100:.1f} % | {np.sqrt((d[pk]**2).mean())/S2[pk].mean()*100:.1f} % | {(m2/m1-1)*100:+.2f} % |\n"
# compute
nh = 0.0; lines = []
for l in open('jobs.log'):
    m = re.search(r'([\d.]+) nh', l)
    if m and not l.startswith('#'): nh += float(m.group(1)); lines.append(l.strip())
tpl = open('scripts/report_template.md').read()
head = (f"| quantity | value | source |\n|---|---|---|\n"
        f"| peak photon energy of the largest invariant M_s(ω) = Σ_αβ |Γ^αβ_s(ω)| in 0–6 eV | **{res['peak_ev']:.2f} eV** | `kernel/Gamma_alphabeta_s.dat` ({adopted}), `scripts/make_result.py` |\n"
        f"| its value (per-mode magnitude summed over the 9 Cartesian channels) | **{res['peak_a2_per_ev']:.3f} Å²/eV** | same |\n"
        f"| dominant phonon mode | **{res['mode_thz']:.4f} THz** ({res['mode_thz']*4.135667696:.3f} meV), irrep **{res['mode_irrep']}** (Γ15, triply degenerate TO/LO optical triplet of zincblende; imode {rows[[r[0] for r in rows].index(int(adopted.split('x')[0]))][3]} of the file) | kernel file header; `remote_out/02_ph/dynmat_gamma.out` |\n"
        f"| adopted fine k-mesh | **{adopted}** (Γ-only q) | `inputs/04_epw/epw2_template.in` |\n"
        f"| compute | **{nh:.2f} node-hours** | `jobs.log` |\n"
        f"| wall time (container start 2026-10-15T09:26Z → DONE) | **{res['wall_hours']:.1f} h** (two interruptions by the model-account usage limit: 10-15 13:38Z→10-16 10:11Z and 10-16 13:15Z→17:07Z are included) | transcript time stamps |\n\n"
        "Invariant convention (decided, see NOTES.md §4): for each optical mode s the rotational invariant is the per-mode magnitude "
        "M_s(ω) = Σ_{αβ} |Γ^{αβ}_s(ω_s; ω, −ω)| over the nine Cartesian channels (complex modulus of each channel); the reported peak is the "
        "maximum of M_s over the optical modes and over the photon grid 0.01–6.00 eV, and the reported mode is the one realising that maximum "
        "(it is also the mode with the largest M_s at that energy). Because the three optical modes are an exactly degenerate T2 triplet, the "
        "individual M_s depend on the basis EPW's diagonaliser picks inside the degenerate subspace; the triplet sum Σ_s M_s and the fully "
        "invariant Frobenius norm √Σ_s Σ_αβ |Γ|² are therefore also tabulated in §6.")
epwsec = ("Fine runs (`remote_out/04_epw/k<N>/epw2_k<N>.out`): epwread from `epwdata.fmt`, `vmedata.fmt`, `03_wan/tmp/gap.epmatwp` (8.9 GB) written by the coarse run "
          "(`remote_out/04_epw/epw1.out`, 128 MPI ranks = pools, 40.7 min). The coarse run reads the ph.x irreducible-q order from `gap.dyn0` "
          "(authors' patch; without it EPW mis-assigns the dvscf files, which crashed the first attempt), the converged set-F Wannier functions from `gap.ukk`, "
          "and evaluates 216 coarse q with the polar long-range correction. Every fine run gives identical mode energies 44.5434 meV (×3) in the "
          "file header. The code also writes `Pi_0.dat` (field-free phonon self-energy) and `epsilon2_*` absorption files, which are not used here.")
comp = ("Total from `jobs.log` (node = 128 cores; shared-node jobs counted as cores × hours / 128): **%.2f node-hours** of the 20 allowed.\n\n```\n%s\n```\n\n"
        "Wall time: container start 2026-10-15T09:26Z to DONE %s = %.1f h, of which ~24.6 h were the two usage-limit interruptions of the model account "
        "(no compute ran during the first; the OOM-killed coarse job 22900599 ran during the second).") % (nh, '\n'.join(lines), sys.argv[2], res['wall_hours'])
conv = (f"Kernel files: `kernel/Gamma_alphabeta_s_<mesh>.dat` for every mesh and `kernel/Gamma_alphabeta_s.dat` = the adopted {adopted} file (byte-identical copy of `remote_out/04_epw/k{adopted.split('x')[0]}/Gamma_alphabeta_s.dat`). Script: `scripts/mesh_convergence.py`.\n\n"
        + tab + diff +
        "\nThe peak is the E1 critical point of GaP: the top valence bands (bands 8, 9) and the first conduction band run parallel along the whole Λ line L→Γ, with a PBE direct transition energy of 2.80 eV at L and 2.81–2.83 eV along Λ (`wannier_vs_dft_bands_setF.dat`; the PBE direct gap at Γ is only 1.84 eV and the Γ E0 transitions give the weak onset near 2.0 eV). This two-dimensional van Hove singularity makes the peak sharp and already stable in position and height from 72³ onwards, while the broad plateau above 3 eV and the weak features at 4–5 eV need the denser meshes "
        "because the 25 meV Gaussian is narrower than the fine-mesh energy spacing of the coarser grids.")
out = tpl.replace('__HEADLINE__', head).replace('__EPWSECTION__', epwsec).replace('__CONVERGENCE__', conv).replace('__COMPUTE__', comp)
open('REPORT.md', 'w').write(out); print("REPORT.md written; node-hours", round(nh, 3))
