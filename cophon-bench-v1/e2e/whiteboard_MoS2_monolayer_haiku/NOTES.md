# NOTES — MoS2 monolayer, light-induced coherent-phonon kernel (cophon-bench v1, whiteboard, haiku)

Start: 2026-10-16 07:04 UTC (folder creation). All times below local (EEST = UTC+3) unless noted.

## Reading (done)
- papers/: manuscript (Eq. Gamma_2nd_final: Gamma^{ab}_s = pi e^2 int[dk] sum_mnl ...; SI sec. MoS2: 12x12x1 k, 90 Ry, "not pursued further").
  The manuscript does NOT define a "rotational invariant" of the kernel. I decide (and state it in REPORT.md):
  I(s,omega) = sqrt( sum_{a,b} |Gamma^{ab}_s(omega)|^2 ) — the Frobenius norm of the 3x3 kernel, invariant under rotations of
  the Cartesian frame, units Å²/eV. Peak = max over (omega in [0,6] eV, s) of I. Mode = the s that attains it at that omega.
- implementation_note.tex: EPW kernel = indabs.f90 (Gamma_c triangle + Pi_0). Input: lindabs=.true., omegamin/omegamax/omegastep in eV,
  degaussw (eV, default 0.025), ladsmear (default false), eps_acoustic (default 0.1 cm-1).
- Toolchain source /scratch/.../toolchain/qe-phnlo-75/EPW/src/indabs.f90:
  * writes Gamma_alphabeta_s.dat: col1 photon energy (eV), then Re,Im of xx,yy,zz,xy,xz,yz,yx,zx,zy (18 cols), units Å²/eV;
    one block per mode, modes imode = 4..nmodes (acoustic 1-3 skipped), header line gives phonon energy in meV.
  * Gamma_alphabeta_s is allocated and zeroed in every q-call and written only at iq == lastq => the file is the contribution of the
    LAST q point. For a Gamma-phonon result the q grid must be Gamma only (nq1=nq2=nq3=1, nqf1=nqf2=nqf3=1).
  * 1/omega^2 prefactor: omega = 0 gives Inf/NaN. Grid must start above zero (omegamin = 0.01 eV).
  * ef0 = efnew (or fermi_energy if efermi_read): set efermi_read=.true. and midgap for the insulator.
- test-suite/epw_2D (MoS2, SOC, Mo:d, wannierize inside EPW) used as template for the EPW input.
- EPW reads dvscf from dvscf_dir/<prefix>.phsave (so dvscf_dir = <ph outdir>/_ph0/).

## Decisions
- Scalar-relativistic PBE, PseudoDojo nc-fr-04 standard Mo.upf/S.upf (task allows), ecutwfc = 90 Ry (Mo normal 80 Ry, high 92 Ry).
- Cell: exactly structure.cif / structure_POSCAR (a = 3.18558 Å, c = 18.12833 Å), no relaxation of the cell.
  Internal coordinates: forces checked in SCF; relax only if the forces are significant.
- SCF k 12x12x1 (as SI). NSCF: full 12x12x1 uniform list in [0,1), nosym, nbnd = 30 (EPW needs explicit list).
- Phonons: ph.x at Gamma only (trans, tr2_ph = 1e-14), ASR applied by dynmat.x / check of acoustic frequencies.
- Queue: `small` (32 of 128 cores). Standard partition had 309 pending jobs. Chained SCF+ph+NSCF into one job (ids in jobs.log).
- Account/ssh user on LUMI is <user> (the toolchain owner). Other jobs in squeue under this account are not mine; not touched.

## Final decisions and outcome (appended at completion)
- Adopted Wannier set A2: Mo:d + S:p (11 WF), exclude bands 1–6, dis window −6.5..7.5 eV, frozen −1.5..2.4 eV. Passed: top VB 0.6 meV RMS, lowest CB 1.0 meV RMS, [VBM−1,CBM+6] 2.5 meV RMS.
- Set A (frozen to 1.3 eV) rejected: lowest CB 32 meV RMS. Set B (12 WF, Mo:s added) cancelled, not needed.
- Kernel mesh series (A2): 48→65.61, 72→63.77, 96→64.01, 120→64.04 Å²/eV at 2.83 eV, mode A'_1 (imode 8, 11.890 THz). Converged 120x120x1.
- Invariant definition: Frobenius norm sqrt(sum_ab |Gamma^ab|^2), units Å²/eV. Alternative sum-of-magnitudes: 90.67 Å²/eV at the same point.
- Workaround: copied ph.x mos2.dvscf1 to mos2.dvscf_q1 for EPW (see REPORT §6).
- Job chain issues (all fixed, logged in jobs.log): outdir paths; EPW epwwrite flag; dvscf_dir CHARACTER(100) truncation; missing mos2.dyn_q1; missing mos2.dvscf_q1 (ph.x electron_phonon=epw needed).
