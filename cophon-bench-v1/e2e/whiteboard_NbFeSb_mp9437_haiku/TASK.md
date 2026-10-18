# Task: compute the light-induced coherent-phonon generation kernel of NbFeSb from first principles

(cophon-bench v1 whiteboard task sheet, NbFeSb_mp9437, model haiku. You run inside a container: this folder is /home/wb/work; the pseudopotential table is
mounted read-only at /home/wb/pseudos; `ssh lumi` is configured. Changes from v0: the cell is sealed, the deliverable is a declared RESULT.json
plus the kernel file at a fixed path, partitions are chosen by queue.)

You are a computational materials scientist with a terminal and access to the LUMI supercomputer. Work alone, from scratch,
in THIS folder only. Nobody will answer questions: decide yourself, write your decisions down, and finish.

## Goal
For the crystal in `structure.cif` (= `structure_POSCAR`; both describe the SAME sealed cell), compute the second-order light-induced
coherent-phonon generation kernel Gamma^{ab}_s(omega_s; omega, -omega) of Hu, Guo, Li, Wang, Chang (manuscript, SI and the authors'
implementation note in `papers/`) for photon energies 0 to 6 eV, for every Gamma-point optical phonon mode s, using the authors'
modified EPW code (the "kernel variant") built on LUMI (see Resources).

**The cell is sealed.** Use the lattice vectors of `structure.cif` exactly as given; do not relax or rescale the cell (no vc-relax).
You may relax the internal coordinates at the fixed cell. Report the cell you used in RESULT.json.

Deliver, in this folder:
1. `RESULT.json` with exactly these keys:
   `{"schema": "cophon-bench.e.result.v1", "material": "NbFeSb_mp9437", "kernel_file": "kernel/Gamma_alphabeta_s.dat",
     "peak_ev": <photon energy of the largest rotational invariant of the kernel between 0 and 6 eV>,
     "peak_a2_per_ev": <its value, Å²/eV, the per-mode magnitudes summed over Cartesian channels as the paper defines the invariant>,
     "mode_thz": <frequency of the phonon mode that dominates the kernel at that energy>, "mode_irrep": "<its irreducible representation>",
     "mesh": "<adopted fine k-mesh, e.g. 96x96x96>", "cell_angstrom": [[..],[..],[..]], "species": [..], "positions_crystal": [[..],..],
     "node_hours": <total compute, from jobs.log>, "wall_hours": <start to DONE>, "model_usd": null, "human_touches": 0}`
2. The kernel output file written by the code, copied to `kernel/Gamma_alphabeta_s.dat` (the converged mesh; keep the coarser meshes
   as `kernel/Gamma_alphabeta_s_<mesh>.dat`), every input file you used (pw.x, ph.x, wannier90, epw.x), the Wannier band comparison data,
   and `jobs.log` with one line per Slurm job: job id, purpose, partition, nodes x hours.
3. `REPORT.md`: the same numbers as RESULT.json with the evidence: mesh convergence (at least two meshes), Wannier interpolation quality
   (DFT vs Wannier bands along a high-symmetry path: RMS and maximum deviation in the valence bands plus conduction bands to ~6 eV above
   the gap), the Gamma phonon frequencies from DFPT with the acoustic sum rule, and the compute used.
4. `NOTES.md`: a running log of what you did and decided, and why.
5. An empty file `DONE` when finished (or `STOPPED` with the reason when you stop early).

## Resources (everything you may use)
- `ssh lumi` works (connection multiplexed; one session at a time is enough). Project account: `project_<id>`.
- Toolchain on LUMI: `/scratch/project_<id>/<user>/theory2code/cphon/toolchain/qe-phnlo-75` = Quantum ESPRESSO 7.5 with the authors' modified EPW (the kernel variant). Binaries under
  its `bin/` (pw.x, ph.x, q2r.x, matdyn.x, dynmat.x, projwfc.x, wannier90.x, pw2wannier90.x, epw.x). The source tree is there too: read EPW's
  source and documentation inside it to learn the input flags of the kernel calculation and the output file it writes. Modules the build
  expects: `module load LUMI partition/C`, `PrgEnv-gnu`, `cray-fftw` (check the tree for a README or env file).
- Pseudopotentials (PseudoDojo, fully relativistic norm-conserving v0.4 standard, UPF) on this machine: `/home/wb/pseudos/nc-fr-04_pbe_standard_upf/nc-fr-04_pbe_standard` (hints with
  cutoffs: `/home/wb/pseudos/djrepo_hints_nc-fr-04_pbe.json`). Copy what you need to the cluster. Scalar-relativistic use (no spin-orbit) is acceptable.
- Your remote root: `/scratch/project_<id>/<user>/theory2code/cphon/bench_whiteboard_v1/NbFeSb_mp9437/` (create it). Work only there.
- Partitions and queues: LUMI-C `small` (shared nodes, up to 4 nodes, 3 days), `standard` (exclusive 128-core nodes, 2 days), `debug` (30 min, 2 jobs per user). Check `squeue -p standard -t PD | wc -l` and `sinfo -p small,standard -o "%P %a %D %T"` before a long job: standard has queued for 5-11 h on busy days while small started within the hour. Check the queue (`squeue`/`sinfo`) before choosing a partition for a long job; prefer the one
  that starts sooner at equal cost. `debug` (30 min, 2 jobs per user, needed by other people's short jobs) only for jobs you expect under
  10 minutes, one at a time. Known quirks of this build: Davidson aborts at thresholds <= 1e-8 (use diago_thr_init 5e-6); EPW needs
  npool = the number of MPI ranks and an explicit NSCF k-point list in [0,1); the file-count quota of the project scratch is tight: delete your own large scratch files (wavefunctions) when a step is done; use `sbatch --test-only` to ask the scheduler for an expected start time before choosing between small and standard.

## Budget and rules
- Compute: at most 20 node-hours in total (a full node for one hour = 1 node-hour; shared jobs count by core-hours / cores per node).
  Count it in `jobs.log` as you go; stop and write the report when the budget is reached. Wall-clock: 3 days.
- Work only in this folder and your remote root. Do not read, copy, search or execute anything from any other folder on this machine
  (in particular nothing under <cophon>, ~/2.wan_agentic_workflow, ~/wannier_finale_root,
  ~/wan_campaign, ~/4.memory_control, ~/3.insights4all) or on the cluster outside the toolchain and your root.
  No web access. Do not delete anything outside your root. Do not use other people's reservations.
- Poll jobs no more often than every 2 minutes (`sleep 120`); never run `find` or `du` over trees you did not create.
- Quality you will be judged on (a reference calculation of this crystal in this cell exists and will be compared; you do not get it):
  Wannier bands within a few meV of DFT in the relevant window; DFPT phonons at Gamma with the acoustic sum rule; EPW interpolation on a
  converged fine mesh; the kernel peak converged in the mesh; every number in RESULT.json traceable to a file. The kernel file itself is
  re-analysed by the grader; RESULT.json must agree with it.
Start now: read the papers and the implementation note, inspect the toolchain, plan, then execute. Keep NOTES.md current.
