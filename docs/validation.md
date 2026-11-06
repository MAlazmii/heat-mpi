# Validation and release status

This file distinguishes local evidence from release requirements still pending.
Date: 6 November 2026. Source and executable hashes are stored with local results.

| Requirement | Status | Evidence / limit |
|---|---|---|
| Original coursework protection | PASS for this implementation | New project only; no recovered source copied or modified |
| Mathematical specification | PASS | numerics.md: equations, boundary conditions, timestep, independent references |
| Compiler diagnostics | PASS on Mac and Linux | Both builds use Wall/Wextra/Wpedantic/Wconversion/Wshadow/Werror |
| Serial/MPI correctness | PASS on Mac and Linux | Full-field sine and impulse tests, 1/2/3/4 ranks, uneven partitions and one-row slabs |
| Continuum convergence | PASS on Mac and Linux | Equal-time refinement ratio between 3.8 and 4.2 |
| Failure handling | PASS on Mac and Linux | Invalid inputs, oversized grids, too many ranks, output collisions and missing directories |
| Serial memory safety | PASS for exercised cases | AddressSanitizer/UBSan: 7x5 impulse, 1x1 zero-step sine |
| Benchmark reproducibility | PASS for recorded local and Linux cases | Raw repetitions, build manifests, input/source/binary hashes, full test log; translated execution |
| Multi-node / native cluster performance | NOT RUN | No cluster performance claims |
| Clean rebuild | PASS locally | Separate temporary copy rebuilt and all six test methods plus sanitizer smoke checks passed; results/clean-build-validation.txt |
| Remote Linux workflow | PASS for linked revisions | Ubuntu 24.04 / Open MPI and Ubuntu 26.04 / MPICH; run details below |
| Private GitHub repository | COMPLETE | MAlazmii/heat-mpi created and verified private |
| Public license and release | PENDING | Owner license choice and public-release approval required |

The static independent review found no blocking stencil, halo, decomposition or
gathering issue. It identified compiler-provenance and discarded-test-log defects
in the measurement harness; both were corrected before collecting results.
This is a development candidate, not a certified production or research result.

Full suite: `python3 -m unittest discover -s tests -v`. It uses subprocess timeouts
and fails on missing MPI executables or blocked launches rather than silently skipping.
The seven test methods contain multiple configurations, including benchmark failure diagnostics.

No numerical test guarantees correctness for every allowed grid/step combination.
The 10-million-cell cap is a safety bound, not a verified performance envelope.
Local AddressSanitizer coverage does not claim instrumented MPI-library coverage.

GitHub-preparation review: expanded Ubuntu coverage to Open MPI and MPICH, with
always-uploaded logs/manifests. A failing-command regression test reproduced lost
benchmark diagnostics and passed after correction. Benchmark snapshots now retain
partial samples with status incomplete; only a finished run is marked complete.

## Native Linux evidence

- [Open MPI: Ubuntu 24.04](https://github.com/MAlazmii/heat-mpi/actions/runs/42240499204)
  tested commit `131931c3d4a1524e718b0473ae53f7eefcd3b789`.
- [MPICH: Ubuntu 26.04](https://github.com/MAlazmii/heat-mpi/actions/runs/42239726228)
  tested commit `84b36db76962b600ad9945aa07a466c158f99e41`.

Each linked job passed all seven test methods, serial AddressSanitizer/UBSan checks,
and the exact benchmark workload validation plus three repeated timings for each
of four configurations. Source, tests, scripts and Makefile fingerprints in both
artifacts were compared against the current files and match. Workflow/documentation
revisions differ; the links identify that boundary explicitly. For the latest
whole-commit result, see the repository's Actions page.

The Ubuntu 24.04 MPICH package failed due to its documented PMI configuration defect.
The supported MPICH test environment is Ubuntu 26.04; no claim is made that the
broken package is supported. Numerical tolerances were not relaxed.

Machine-readable evidence: `results/linux-validation-summary.json`. Full downloaded
artifacts are retained locally under `results/ci/`; GitHub retains each for 14 days.
No paid usage, subscription, spending-limit increase or premium runner was enabled.
