# GitHub readiness

Repository: **MAlazmii/heat-mpi**.
Description: Reproducible C/MPI heat-diffusion solver with analytical validation and benchmark provenance.
License: [MIT](../LICENSE). Public release authorized by the owner on 6 November 2026.

## Prepared contents

- C11 serial/MPI source and independent numerical tests.
- Build tooling and source/executable provenance records.
- README, method specification, development guidance, validation limits and generated illustration.
- Ubuntu 24.04 / Open MPI and Ubuntu 26.04 / MPICH workflows, strict warnings, complete integration
  tests, serial AddressSanitizer/UBSan, and the benchmark pipeline.
- Workflow logs/build manifests retained for 14 days, associated with the exact commit.
- Pinned third-party Actions and read-only workflow repository permissions.

Compiled binaries and local benchmark metadata are excluded. Original coursework,
Blackboard materials and recovered supercomputer directories are outside this repository.
Remote: https://github.com/MAlazmii/heat-mpi. The candidate files were scanned for common token/private-key patterns, personal
absolute paths and student identifiers, with no matches. This bounded scan is not
a universal secret-detection guarantee. CI configuration received an independent
static review.

## Linux execution status

Both MPI implementations have passed native Linux numerical tests, serial sanitizers
and benchmark reproduction. Test scope and source fingerprints are recorded in
[validation](validation.md) and `results/linux-validation-summary.json`.
The [Actions page](https://github.com/MAlazmii/heat-mpi/actions/workflows/ci.yml)
provides the checks and artifacts for each uploaded revision. Downloaded
logs and raw results are preserved locally under ignored `results/ci/` directories.

Ubuntu 24.04's MPICH 4.2.0-5build3 initially reproduced a documented distribution
packaging defect: launched processes each saw rank zero in a one-process communicator.
Tests rejected it. Ubuntu 26.04's MPICH 4.3.2 passed. Package download retries and
timeouts are bounded to limit stalled runner time.

References: [runner-image report](https://github.com/actions/runner-images/issues/13204),
[Ubuntu package bug](https://bugs.launchpad.net/ubuntu/+source/mpich/+bug/2072338).
No numerical tolerances were relaxed and no failing tests were disabled.

Included Actions capacity was verified before launch. No billing settings, paid
runner options, spending limits or subscriptions were changed.

## Release requirements

The owner selected MIT and authorized public visibility. Publication requires a
reviewed source tree, private commit email addresses and successful checks for the
exact release revision. Tagged versions should meet the same requirements.
No multi-node performance claim follows from GitHub’s single-host runners.

Local preflight: all seven test methods passed; the revised benchmark completed
three repeats for each of serial and 1/2/4 MPI ranks. Source/executable fingerprints
match the tested files. Serial sanitizer checks also passed in this preparation.
