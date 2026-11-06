# GitHub readiness

Prepared repository: **MAlazmii/heat-mpi** (proposed name).
Description: Reproducible C/MPI heat-diffusion solver with analytical validation and benchmark provenance.
Initial visibility: **private**, pending authorization to create/upload.

## Prepared contents

- C11 serial/MPI source and independent numerical tests.
- Build tooling and source/executable provenance records.
- README, method specification, development guidance, validation limits and generated illustration.
- Ubuntu 24.04 workflow for Open MPI and MPICH, strict warnings, complete integration
  tests, serial AddressSanitizer/UBSan, and the benchmark pipeline.
- Workflow logs/build manifests retained for 14 days, associated with the exact commit.
- Pinned third-party Actions and read-only workflow repository permissions.

Compiled binaries and local benchmark metadata are excluded. Original coursework,
Blackboard materials and recovered supercomputer directories are outside this repository.
The repository has no remote yet. The candidate files were scanned for common token/private-key patterns, personal
absolute paths and student identifiers, with no matches. This bounded scan is not
a universal secret-detection guarantee. CI configuration received an independent
static review.

## Linux execution status

NOT RUN. This Mac has no detected Docker/Podman/Lima/QEMU runtime. GitHub hosted
runners are the selected route; GitHub authentication was verified with network
access. Creation/upload of a private repository requires the owner's approval.
Private Actions runs may consume the account's included minutes; do not enable paid
overages or purchase runner capacity. Check account availability before launch.
A workflow definition is not evidence of Linux success.

## Release gates after the private test run

1. Inspect both MPI jobs and artifacts for the exact pushed commit; fix failures and rerun.
2. Record Linux results in docs/validation.md with run links and tested revision.
3. Choose a public license. No license is silently selected by this preparation.
4. Review public contents and authorize public visibility separately.
5. Tag a release only after required checks pass. No multi-node performance claim
   follows from GitHub's single-host runners.

Local preflight: all seven test methods passed; the revised benchmark completed
three repeats for each of serial and 1/2/4 MPI ranks. Source/executable fingerprints
match the tested files. Serial sanitizer checks also passed in this preparation.
