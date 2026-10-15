# NOTES.md — NbFeSb coherent-phonon generation kernel (running log)

Started 2026-10-14 (local evening). Agent works alone; all decisions recorded here.

## 0. Reading (what the code actually computes)
- Manuscript Eq. (Gamma_2nd_final): second-order kernel Gamma^{ab}_s(omega_s; omega, -omega) = diagram (c) [Raman-like
  triangle, g * h * h] + diagram (e) [g^{s;a} * h, optically perturbed EPC vertex]. Electronic broadening eta = 0.025 eV
  (SI Sec. IV A "Methods"). Band-pair resonance delta(hbar*omega - eps_nm).
- The LUMI build `qe-phnlo-75/EPW/src/indabs.f90` ("kernel variant") implements, inside `indabs_main`, the block
  "Coherent-phonon generation kernel (Gamma_c triangle + Pi_0), v1 scope": only diagram (c) + the field-free phonon
  self-energy Pi_0. Diagram (e) (`lgammae`, epvf17) is declared "out of scope in v1" -> NOT computed by this build.
  -> Decision: deliver what the kernel variant computes (Gamma_c) and say so explicitly in REPORT.md.
- Trigger: `lindabs = .true.` (phonon-assisted-absorption driver). Photon grid: omegamin/omegamax/omegastep (eV).
  Broadening: `degaussw` (Gaussian delta via w0gauss(...,0) and the i*eta in the 1/(omega_s+eps_ln+i*eta) propagator).
  Optional `ladsmear` (adaptive smearing from band-velocity differences, floored at 1 meV).
  Occupations: step function at ef0 (= fermi_energy if efermi_read). Bands: nbndfst = bands inside +-fsthick of Ef.
- Output: `Gamma_alphabeta_s.dat` (header: photon energy (eV), then Re/Im of xx,yy,zz,xy,xz,yz,yx,zx,zy in ang^2/eV,
  one block per optical mode imode=4..nmodes, with phonon energy in meV) and `Pi_0.dat`. Written once, at the last q.
- Prefactor contains 1/omega^2 -> omegamin must be > 0 (omega = 0 would give Inf/NaN). Use omegamin = omegastep.
- Only the q = Gamma phonon enters. The kernel needs g(k, q=Gamma), h^a(k) on a fine k mesh (no q interpolation).

## 1. Material facts
- NbFeSb half-Heusler, F-43m (T_d), fcc primitive cell a_prim = 4.20116 A (a_conv = 5.94134 A). 3 atoms -> 9 modes:
  at Gamma: T2 (acoustic) + 2 x T2 (optical, both IR+Raman active, each triply degenerate). Nonmagnetic semiconductor.
- PseudoDojo nc-fr-04 standard: Nb (13 e, 4s4p semicore), Fe (16 e, 3s3p semicore), Sb (15 e, 4d semicore) -> 44 e
  -> 22 occupied bands (13 semicore + 9 valence). Cutoff hints (normal/high Ry): Nb 82/98, Fe 90/106, Sb 80/88.
  -> ecutwfc = 90 Ry (paper also used 90 Ry), ecutrho = 360 Ry. Scalar-relativistic use (no SOC), as allowed.

## 2. Plan (budget 20 node-hours; count in jobs.log)
1. SCF pw.x, 8x8x8 k, 90 Ry.                                   (~0.1 NH)
2. ph.x at Gamma only (ldisp, nq=1x1x1, epsil=.true. for Z* and eps_inf), tr2_ph=1e-16; dynmat.x with ASR -> Gamma freqs.
3. NSCF on the full 8x8x8 grid (explicit list in [0,1)), nbnd ~ 50; pw.x bands along W-L-G-X-W-K for the DFT reference.
4. EPW run A: Wannierize inside EPW (nbndsub chosen after inspecting bands), band_plot along the same path -> compare.
5. EPW run B (epwread): fine k meshes (>= 2, e.g. 48^3, 64^3, 80^3 [, 96^3]), q = Gamma only, lindabs, 0.025..6 eV.
6. Post-process Gamma_alphabeta_s.dat -> rotational invariant per mode; peak; dominant mode; mesh convergence.
Rules: debug partition only for < 10 min jobs; poll every >= 120 s; delete wfc files when done.

## 3. Execution log
- 2026-10-14 ~22:50 (LUMI time): submitted SCF (22844845), ph.x Gamma (22844846, afterok), NSCF (22844847, afterok) on
  `standard` (1 node each; small partition was crowded, standard had >100 idle nodes). Inputs in `inputs/`.
  Decisions: ibrav=0 with the POSCAR cell so Cartesian axes = the given structure's axes (kernel components refer to them);
  SCF k 10x10x10 unshifted; coarse EPW grid = same 10x10x10 (1000 k, explicit list in [0,1), nosym); nbnd=60 in NSCF
  so the Wannier disentanglement window can extend well above CBM+6 eV; conv_thr 1e-10 SCF; NSCF/bands use
  diago_thr_init=5e-6 as the build note advises. tr2_ph=1e-16 (paper value). epsil=.true. to get eps_inf and Z* (LO-TO
  reported via dynmat.x with a q direction; the kernel itself uses the exact-Gamma TO/analytic dynamical matrix).
- Why q-grid 1x1x1 for DFPT/EPW: the kernel involves only the Gamma phonon; EPW then interpolates g(k,q=Gamma) and
  h^a(k) in k only (q-interpolation would be exact anyway at q=Gamma). Saves DFPT cost; nothing is lost for this target.

## 4. Definitions fixed before seeing any kernel numbers
- "Rotational invariant" (task wording: per-mode magnitude summed over the Cartesian channels). The paper plots |Gamma^{ab}_s|
  per channel (Fig. captions) and uses an isotropic field E^{a,b}=E_0 in SI Sec. IV A; it does not name an invariant
  explicitly. I adopt S1_s(omega) = sum_{a,b=x,y,z} |Gamma_s^{ab}(omega)| (9 channels, complex magnitudes) as the headline
  quantity, and also tabulate F_s = sqrt(sum_ab |Gamma^{ab}|^2) and A_s = |sum_ab Gamma^{ab}| (isotropic-field combination)
  so a reader using another convention can read off their number. The peak photon energy is the main answer; all
  definitions are reported at that energy. Script: scripts/kernel_invariants.py.
- Degenerate modes: T_d gives two triply degenerate T2 optical triplets. Individual partners within a triplet depend on the
  (arbitrary) eigenvector basis chosen by the diagonalizer; the sum over the triplet is basis independent for quadratic
  invariants. I report per-mode values AND the triplet sums.
- Broadening: degaussw = 0.025 eV as in the paper (Gaussian delta via w0gauss(...,0): exp(-x^2)/sqrt(pi), FWHM = 41.6 meV).
- Fine k-mesh: fixed 25 meV broadening in 3D cannot be resolved point-wise on any affordable mesh (ΔE ~ v Δk ~ 0.1 eV at 64^3),
  but the kernel is a sum over many transitions, so the spectrum converges statistically. Plan: measure cost on a small mesh,
  then run >= 3 meshes (target 48^3, 64^3, 80^3, 96^3 if affordable) and report the peak energy/value vs mesh.
  Optionally cross-check with the code's adaptive smearing (ladsmear) on one mesh.
- Photon grid: omegamin = omegastep = 0.025 eV, omegamax = 6.0 eV (240 points). omega = 0 excluded (1/omega^2 prefactor).
- SCF done (job 22844845, 29 s wall on 1 node): 24 sym ops (T_d, no inversion), 47 irreducible k, E_tot converged in 14
  iterations, VBM 16.4886 eV, CBM 17.0158 eV -> PBE gap 0.527 eV (indirect: VBM at L [k#137], CBM at X [k#25] on the path).
  Band characters (projwfc, results/dft/projwfc.out): bands 1-13 semicore (Fe3s -69.7, Nb4s -38.3, Fe3p -35.8, Nb4p -14.4,
  Sb4d -12.2 eV); band 14 = Sb 5s (5.1-6.9 eV); 15-22 = Sb p + Fe/Nb d (valence); 23-27 = Nb d/Fe d conduction (17.0-22 eV);
  28 = Nb s/Sb p (20.2-23.5); >= 29 free-electron-like (projectability < 0.5). Along the path at most 17 non-semicore
  bands lie below CBM+6 eV = 23.02 eV (bands 29/30 dip to 22.62 eV).
- Wannier model candidates (all with exclude_bands 1-13, outer window from 4.0 eV):
  A16: Nb s,d + Fe s,d + Sb s,p (16 WFs), frozen 4.0-22.3 eV (= VBM+5.8 eV; the 17th band starts at 22.62 eV), outer max 28.
  B19: A16 + Fe p, frozen to 24.5 eV, outer max 32.    C22: Nb s,p,d + Fe s,p,d + Sb s,p, frozen to 26.0, outer max 36.
  Selection rule: smallest RMS/max deviation vs DFT in [5, 23.0] eV along the path (scripts/band_compare.py); prefer the
  smaller model if errors are comparable (kernel cost ~ nb^3). All three run in one job (22845130).
- EPW settings fixed: vme='wannier' (the authors' vmewan2bloch route, uses the Wannier position matrix), use_ws=.false.
  (the authors' modified routines index cfac(:,1,1), i.e. assume no WS-distance dims), lpolar=.false. (at q=Gamma exactly
  the long-range terms vanish in EPW anyway), asr_typ='crystal', efermi_read with fermi_energy = mid-gap 16.7522 eV,
  fsthick=100 eV (all Wannier bands enter the band sums), degaussw=0.025 eV.
- ph.x at Gamma done (job 22844846, 96 s wall): T_d point group, 3 irreps (all T_2, I+R active). Raw DFPT: acoustic
  5.79 cm-1, optical 204.81 and 263.41 cm-1. dynmat.x with asr='crystal' (results/phonons/dynmat.out):
  modes 4-6: 204.81 cm-1 = 6.1399 THz (IR 1.80 (D/A)^2/amu); modes 7-9: 263.32 cm-1 = 7.8942 THz (IR 29.80).
  ||dyn(ASR)-dyn(orig)|| = 1.2e-3. eps_inf = 24.43 (isotropic); Z*(ASR): Nb +5.053, Fe -7.623, Sb +2.571 (sum ~0).
  With a q direction (dynmat_LO.out, q||x): LO partners 207.33 cm-1 (6.216 THz) and 347.73 cm-1 (10.425 THz).
  The kernel run uses the exact-Gamma (analytic, TO-degenerate) modes from EPW.
- NSCF done (job 22844847, 25 s wall): 1000 k, 60 bands.
- pp.py (EPW/bin/pp.py, not bin/) must be run inside the ph.x outdir (needs ./_ph0 and ./nbfesb.save) with the dyn files
  linked there; done on the login node (file copies only); save/ moved to the run root. save/ has nbfesb.dvscf_q1,
  nbfesb.dyn_q1, nbfesb.phsave/{patterns.1.xml,...}.
- EPW coarse job 22845130 done (40 min, 0.67 NH; 12-16 min per model, dominated by the 1000-k Wannierization + g transform).
  Wannier-vs-DFT along the path (scripts/band_compare.py, results/epw/<model>/band_compare_*.dat), window [5.0, 23.02] eV
  (= Sb-5s band bottom ... CBM+6 eV), 13 semicore bands skipped:
    A16: RMS 9.17 meV, max 155 meV (band 28 near 22.9 eV, outside its frozen window 22.3 eV; valence-only RMS 2.5 meV)
    B19: RMS 62 meV, max 0.80 eV  -> disentanglement failed (one WF spread 11 A^2); discarded
    C22: RMS 0.61 meV, max 4.88 meV (band 28 at 21.6 eV); valence [5,16.5]: RMS 0.53 / max 2.9 meV; conduction [17,23.02]:
         RMS 0.71 / max 4.9 meV. Omega_total = 42.1 A^2 (22 WFs, largest spreads ~3 A^2).
  DECISION: use C22 (Nb s,p,d + Fe s,p,d + Sb s,p; frozen 4.0-26.0 eV, outer 4.0-36.0 eV) for the kernel. Cost of the
  kernel loop grows as nb^3 (22^3 = 10648) but accuracy wins; the paper's SnSe model also used 28 bands.
- EPW Gamma phonon energies after its (simple) ASR: 25.3934 meV x3 and 32.6239 meV x3 (= 204.81 and 263.13 cm-1), i.e.
  within 0.2 cm-1 of dynmat.x 'crystal' ASR (263.32). Fermi level read as 16.7522 eV (mid-gap).
- Pitfall found: EPW writes prefix.epmatwp into outdir; the three coarse runs shared outdir ../tmp_nscf so the file was
  overwritten three times; the last writer was C22 (checked by timestamp/size) - the model adopted anyway.
- Kernel run k=24^3 (job 22846845, 114 s on 1 node; ~0.9 s per k-point per MPI rank, all in the indabs loops):
  Gamma_alphabeta_s.dat written for modes 4-9 (results/kernel/k24). Sanity: (i) tensor structure = T_2 of T_d: each mode has
  one dominant off-diagonal pair with equal magnitude (xy=yx, xz=zx or yz=zy), diagonal xx,yy,zz ~1e-2 (numerical noise of
  the coarse mesh), the partners of a triplet mix channels (arbitrary degenerate basis); (ii) below the direct gap the
  kernel is ~1e-30 (exactly the Gaussian tails); (iii) direct absorption (epsilon2_dirabs) onset ~1.13 eV = direct gap
  (indirect gap 0.53 eV); (iv) EPW used ibndmin=1..ibndmax=22 (all Wannier bands), Ef = 16.7522 eV.
  First look (24^3, NOT converged): all modes peak at 3.275 eV; S1 (sum of 9 channel magnitudes): modes 7-9
  (32.62 meV = 263 cm-1 triplet) ~ 20-24 A^2/eV each, modes 4-6 (25.39 meV) ~ 13-17 A^2/eV.
- Cost extrapolation: 48^3 ~ 13 min, 64^3 ~ 32 min, 80^3 ~ 1 h, 96^3 ~ 1.8 h (1 node each). Submitted 80^3 and 96^3 plus an
  adaptive-smearing (ladsmear=.true.) cross-check at 64^3. Worst case (all hit their limits) adds ~8 NH; expected ~4 NH.
- Kernel runs 48^3 (job 22846846, 14 min) and 64^3 (job 22846847, 30 min) done; results/kernel/k48, k64.
  Mesh convergence (scripts/mesh_convergence.py): peak of the total S1 (sum over the 6 optical modes) at 3.275 eV on
  24^3, 48^3 and 64^3; total S1 at the peak 114.49 / 114.30 / 114.05 A^2/eV; triplet sums at the peak (modes 4-6 | 7-9):
  45.4|69.1, 47.0|67.3, 46.9|67.1. Relative RMS of the total S1 spectrum over 1-6 eV vs 64^3: 24^3 10.0 %, 48^3 1.9 %.
  Every optical mode peaks at the same photon energy; the 263 cm-1 triplet (modes 7-9) dominates (~23.5-23.8 A^2/eV per
  mode for the two partners that carry the strongest single channel; Frobenius norms 12.2-12.5 vs 8.1-8.4 for modes 4-6).
- The peak is sharp on the 25 meV photon grid (total S1: 54 at 3.225, 93 at 3.25, 114 at 3.275, 97 at 3.30 eV), i.e. a
  resonance of width ~ the 25 meV broadening. To pin its position, zoom runs 3.0-3.6 eV in 5 meV steps on 64^3 and 96^3
  were submitted (same inputs otherwise).
- Origin of the 3.275 eV peak (DFT bands along the path, results/dft/dft_bands_path.dat): vertical transitions within
  ~30 meV of 3.275 eV with zero slope along the path occur for bands 22->27 at X (3.269 eV), 20->25 at L (3.248 eV),
  18->23/24 on Gamma-L (3.29 eV) and 19->24 on K-Gamma (3.268 eV), i.e. a cluster of critical points of the joint
  density of states of the upper valence bands (Fe/Nb d) into conduction bands 23-27 (Nb d). This explains why the peak is
  resonance-like (width ~ broadening) and common to all modes. Not required for the deliverable; recorded for context.
- 2026-10-15 ~02:00: 80^3 full run (job 22847078, 59 min), 64^3 adaptive-smearing run (22847080, 60 min), zoom runs
  3.0-3.6 eV / 5 meV on 64^3 (22848228, 19 min) and 96^3 (22848229, 62 min) done. 96^3 full run (22847079) still running.
  Mesh convergence of the fixed-eta (25 meV) kernel, total S1 at the 25-meV-grid peak (3.275 eV):
    24^3 114.49 | 48^3 114.30 | 64^3 114.05 | 80^3 113.99 A^2/eV ; relRMS of the 1-6 eV total-S1 spectrum vs 80^3:
    10.1 % | 1.85 % | 0.90 % | 0.  Per-mode peak energies identical (3.275 eV) on all meshes.
  Zoom (5 meV grid): total S1 peaks at 3.275 eV (64^3: 114.05) and 3.270 eV (96^3: 114.13); adjacent points 3.270/3.275
  differ by 0.02 % -> peak photon energy 3.27 eV (+-5 meV). Per-mode peaks: modes 4-6 at 3.275, modes 7-9 at 3.270 eV on
  both meshes. FWHM of the total-S1 peak 0.17 eV. 64^3 vs 96^3 zoom spectra differ by 0.3 % RMS over 3.0-3.6 eV.
  At the peak (96^3 zoom, 3.270 eV): modes 7-9 (32.62 meV, 263 cm-1, 7.894 THz): S1 = 23.56 / 23.81 / 19.89, F = 12.18 /
  12.48 / 12.30 A^2/eV; modes 4-6 (25.39 meV, 205 cm-1): S1 = 16.64 / 13.13 / 17.10, F = 8.04 / 8.19 / 8.38 A^2/eV.
  Triplet sums at the peak: S1 = 67.26 (7-9) and 46.87 (4-6); sqrt(sum F^2) = 21.34 and 14.21; equivalently a
  symmetry-adapted partner carries a single off-diagonal channel pair |Gamma^{xy}| = |Gamma^{yx}| = 8.71 (7-9) / 5.80 (4-6).
  Tensor structure at the peak: only off-diagonal channels are significant (|xx|,|yy|,|zz| <= 0.44 vs 8.7), as T_2 of T_d
  requires; the partners are rotated within each degenerate triplet by the diagonalizer (basis-dependent S1, basis-
  independent F and triplet sums).
  Adaptive-smearing cross-check (ladsmear, 64^3): peak at 3.250 eV, total S1 138.6 (narrower effective delta -> taller,
  slightly shifted peak); used only as a sensitivity check of the peak position (shift 25 meV = one 25-meV grid step).
- 2026-10-15 02:39: 96^3 full run done (job 22847079, 99 min, 1.652 NH). Peak at 3.275 eV on the 25 meV grid; total S1
  114.11; triplet sums 46.89 / 67.22; relRMS of the 1-6 eV total-S1 spectrum vs 96^3: 24^3 10.1 %, 48^3 1.75 %, 64^3 0.79 %,
  80^3 0.58 %. Peak value 80^3 -> 96^3: +0.1 %. ADOPTED: 96^3 (densest; converged to < 1 % in the spectrum, < 0.2 % at the peak).
  Total compute 6.46 NH of 20. Final numbers written to REPORT.md; results/kernel/mesh_convergence.txt regenerated.

## 5. Closing (2026-10-15 ~02:50 EEST)
Delivered: REPORT.md (peak 3.27 eV; dominant mode = upper T_2 triplet 263.3 cm-1 / 7.894 THz; invariants at the peak;
fine mesh 96^3 adopted with 24^3-96^3 convergence evidence; Wannier quality RMS 0.61 / max 4.9 meV over valence+CBM+6 eV;
DFPT Gamma frequencies with ASR; 6.46 node-hours), kernel outputs results/kernel/*/Gamma_alphabeta_s.dat (+ Pi_0.dat),
all inputs (inputs/), Wannier-vs-DFT data (results/epw/wanC22/, results/dft/dft_bands_path.dat), jobs.log.
Caveats stated in the report: (1) this build's kernel = diagram (c) only (Gamma_c); diagram (e) is not implemented in
the active indabs.f90 ("out of scope in v1"); (2) scalar-relativistic treatment (no SOC); (3) exact-Gamma (TO-degenerate)
phonons, no LO-TO direction; (4) the per-partner split of a degenerate T_2 triplet depends on the eigenvector basis, so
basis-independent triplet quantities are reported alongside.
LUMI clean-up: SCF/NSCF wavefunctions deleted (tmp/nbfesb.save/wfc*, tmp_nscf/nbfesb.save/wfc*); kept: save/, the Wannier
representation (wanC22/*.fmt, tmp_nscf/nbfesb.epmatwp + backup) and all run outputs under the remote root.
Wall-clock used: ~5.5 h (22:30 Oct 14 - 02:50 Oct 15 EEST), most of it queue waiting.
