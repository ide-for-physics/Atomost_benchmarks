# Task: compute the light-induced coherent-phonon generation kernel of GaP from first principles

You are a computational materials scientist with a terminal and access to the LUMI supercomputer. Work alone, from scratch,
in THIS folder only. Nobody will answer questions: decide yourself, write your decisions down, and finish.

## Goal
For the crystal in `structure.cif` (= `structure_POSCAR`), compute the second-order light-induced coherent-phonon generation
kernel Gamma^{ab}_s(omega_s; omega, -omega) of Hu, Guo, Li, Wang, Chang (manuscript, SI and the authors' implementation note in
`papers/`) for photon energies 0 to 6 eV, for every Gamma-point optical phonon mode s, using the authors' modified EPW code
(the "kernel variant") that is built on LUMI (see Resources). Deliver:
1. `REPORT.md`: the photon energy (eV) at which the rotational invariant of the kernel (the per-mode magnitude summed over the
   Cartesian channels, as the paper defines it) is largest between 0 and 6 eV, its value, the dominant phonon mode at that energy
   (frequency in THz, irreducible representation), the adopted fine k-mesh and the evidence that the kernel is converged with
   respect to it (at least two meshes), the Wannier interpolation quality (DFT bands versus Wannier-interpolated bands along a
   high-symmetry path: RMS and maximum deviation in the window of valence bands plus conduction bands up to about 6 eV above the
   gap), the Gamma phonon frequencies from DFPT with the acoustic sum rule, and the total compute used (node-hours).
2. The kernel output file(s) written by the code, every input file you used (pw.x, ph.x, wannier90, epw.x), the Wannier band
   comparison data, and `jobs.log` with one line per Slurm job: job id, purpose, partition, nodes x hours.
3. `NOTES.md`: a running log of what you did and decided, and why.
4. An empty file `DONE` when you are finished (or `STOPPED` with the reason when you stop early).

## Resources (everything you may use)
- `ssh lumi` works (connection multiplexed; one session at a time is enough). Project account: `project_<id>`.
- Toolchain on LUMI: `/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75` = Quantum ESPRESSO 7.5 with the
  authors' modified EPW (the kernel variant). Binaries under its `bin/` (pw.x, ph.x, q2r.x, matdyn.x, dynmat.x, projwfc.x,
  wannier90.x, pw2wannier90.x, epw.x). The source tree is there too: read EPW's source and documentation inside it to learn the
  input flags of the kernel calculation and the output file it writes. Modules the build expects: `module load LUMI partition/C`,
  `PrgEnv-gnu`, `cray-fftw` (check the tree for a README or env file).
- Pseudopotentials (PseudoDojo, fully relativistic norm-conserving v0.4 standard, UPF) on this machine:
  `~/sc_agentic_workflow/software/pseudos/pseudo_dojo/nc-fr-04_pbe_standard_upf/nc-fr-04_pbe_standard` (hints with cutoffs:
  `~/sc_agentic_workflow/software/pseudos/pseudo_dojo/djrepo_hints_nc-fr-04_pbe.json`). Copy what you need to LUMI.
  Scalar-relativistic use of these pseudopotentials (no spin-orbit) is acceptable.
- Your remote root on LUMI: `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard/GaP/` (create it). Work only there.
- LUMI-C partitions: `small` (shared nodes, up to 4 nodes, 3 days), `standard` (exclusive 128-core nodes, 2 days). `debug`
  (30 min, 2 jobs per user, needed by other people's short jobs) only for jobs you expect under 10 minutes, one at a time.
  Known quirks of this build: Davidson aborts at thresholds <= 1e-8 (use diago_thr_init 5e-6); EPW needs npool = the number of
  MPI ranks and an explicit NSCF k-point list in [0,1); the file-count quota of the project scratch is tight: delete your own
  large scratch files (wavefunctions) when a step is done.

## Budget and rules
- Compute: at most 20 node-hours of LUMI in total (a full 128-core node for one hour = 1 node-hour; shared jobs count by
  core-hours / 128). Count it in `jobs.log` as you go; stop and write the report when the budget is reached. Wall-clock: 3 days.
- Work only in this folder and your remote root. Do not read, copy, search or execute anything from any other folder on this
  machine (in particular nothing under ~/9.coherent_phonon, ~/2.wan_agentic_workflow, ~/wannier_finale_root,
  ~/wan_campaign, ~/4.memory_control, ~/3.insights4all) or on LUMI outside the toolchain and your root.
  No web access. Do not delete anything outside your root. Do not use other people's reservations.
- Poll jobs no more often than every 2 minutes (`sleep 120`); never run `find` or `du` over trees you did not create.
- Quality you will be judged on (a reference calculation of this crystal exists and will be compared, you do not get it):
  Wannier bands within a few meV of DFT in the relevant window; DFPT phonons at Gamma with the acoustic sum rule; EPW interpolation
  on a converged fine mesh; the kernel peak converged in the mesh; every number in REPORT.md traceable to a file.
Start now: read the papers and the implementation note, inspect the toolchain, plan, then execute. Keep NOTES.md current.
