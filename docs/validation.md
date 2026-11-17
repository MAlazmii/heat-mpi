# Validation and release status

This file records validation evidence and its limits.
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
| Benchmark reproducibility | PASS for recorded local and Linux cases | Raw repetitions, build manifests, input/source/binary hashes, full test log |
| Multi-node / native cluster performance | NOT RUN | No cluster performance claims |
| Clean rebuild | PASS on Linux | Each MPI job builds from scratch before running all seven test methods |
| Remote Linux workflow | PASS for recorded source fingerprints | Ubuntu 24.04 / Open MPI and Ubuntu 26.04 / MPICH; run details below |
| Public license | MIT | Owner selected the license and authorized publication; exact revision checks are required before publication |

The static independent review found no blocking stencil, halo, decomposition or
gathering issue. It identified compiler-provenance and discarded-test-log defects
in the measurement harness; both were corrected before collecting results.
This is an educational implementation, not a certified production or research result.

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

Open MPI on Ubuntu 24.04 and MPICH on Ubuntu 26.04 each passed all seven test
methods, serial AddressSanitizer/UBSan checks, and the exact benchmark workload
validation plus three repeated timings for each of four configurations.
The source, tests, scripts and Makefile fingerprints identify the files used in
those runs. Later fixes made the grid-size check overflow-safe and made chart
creation refuse an existing destination atomically. The recorded timings and
checks remain tied to the historical revision.

Use the [numerical-validation workflow](https://github.com/MAlazmii/heat-mpi/actions/workflows/ci.yml)
to inspect the result for a particular commit. A green result applies to the commit
shown on that run; it is not a claim that every future revision passes. Downloadable
artifacts include the tested commit, full test output, toolchain details, build
manifests and raw timing samples. Earlier validation evidence is archived locally.

The Ubuntu 24.04 MPICH package failed due to its documented PMI configuration defect.
The supported MPICH test environment is Ubuntu 26.04; no claim is made that the
broken package is supported. Numerical tolerances were not relaxed.

Machine-readable evidence: `results/linux-validation-summary.json`. Full downloaded
artifacts are retained locally under `results/ci/`; GitHub retains each for 14 days.
No paid usage, subscription, spending-limit increase or premium runner was enabled.

## Local review on 17 November 2026

After the grid-size and chart-output fixes, strict serial/MPI builds and all seven
test methods passed with Open MPI 5.0.6. Both executables were x86_64 builds running
under translation on Apple M1. Native ARM64 serial AddressSanitizer/UBSan checks
passed for the two documented cases. The benchmark pipeline completed three
repetitions for serial and each of 1/2/4 MPI ranks.

Four serial workloads, including the illustrated 63-by-47 grid after 2,000 steps,
produced byte-identical CSV fields before and after the grid-size fix. The limit
formula agreed with exact integer multiplication for one million sampled dimension
pairs, including a product that wraps below the cap in 32-bit arithmetic. Native
32-bit execution remains unverified.

With Matplotlib 3.11.0 and Pillow 13.0.0 in a clean Python 3.11 environment, chart
creation passed new-file, existing-file, symlink, dangling-symlink and suffixless-path
checks. An unsupported format failed without creating an output file. These local
checks supplement the commit-specific Linux workflow results.
