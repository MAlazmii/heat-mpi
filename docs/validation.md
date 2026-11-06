# Validation and release status

This file distinguishes local evidence from release requirements still pending.
Date: 6 November 2026. Source and executable hashes are stored with local results.

| Requirement | Status | Evidence / limit |
|---|---|---|
| Original coursework protection | PASS for this implementation | New project only; no recovered source copied or modified |
| Mathematical specification | PASS | numerics.md: equations, boundary conditions, timestep, independent references |
| Compiler diagnostics | PASS locally | Both builds use Wall/Wextra/Wpedantic/Wconversion/Wshadow/Werror |
| Serial/MPI correctness | PASS locally | Full-field sine and impulse tests, 1/2/3/4 ranks, uneven partitions and one-row slabs |
| Continuum convergence | PASS locally | Equal-time refinement ratio between 3.8 and 4.2 |
| Failure handling | PASS locally | Invalid inputs, oversized grids, too many ranks, output collisions and missing directories |
| Serial memory safety | PASS for exercised cases | AddressSanitizer/UBSan: 7x5 impulse, 1x1 zero-step sine |
| Benchmark reproducibility | Local evidence | Raw repetitions, build manifests, input/source/binary hashes, full test log; translated execution |
| Multi-node / native cluster performance | NOT RUN | No cluster performance claims |
| Clean rebuild | PASS locally | Separate temporary copy rebuilt and all six test methods plus sanitizer smoke checks passed; results/clean-build-validation.txt |
| Remote Linux workflow | NOT RUN | Open MPI + MPICH matrix prepared; execution pending private upload approval |
| Public license and release | PENDING | Owner license choice, public-content review and verified release CI required |

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
