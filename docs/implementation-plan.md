# Heat MPI Implementation Plan

Goal: a reproducible C11 serial/MPI heat-equation solver with independent correctness evidence.
Architecture: explicit five-point stencil on a unit square, zero Dirichlet boundaries,
row decomposition (including uneven slabs), blocking Sendrecv halos, root CSV export.
This is new code from the mathematical specification below, not copied coursework.
Execution is inline under the user's approval of the portfolio plan.

## Specification and choices
Solve u_t = u_xx + u_yy. Interior nx by ny points; dx=1/(nx+1), dy=1/(ny+1).
Initial conditions: sine sin(pi*x)sin(pi*y), or a unit impulse at the central grid point.
Sine continuum reference: exp(-2*pi*pi*t) sin(pi*x)sin(pi*y).
Time step dt=0.2/(1/dx^2+1/dy^2), safely inside the explicit stability limit.
Serial and MPI builds use the same stencil; Python independently validates small fields
and the exact discrete sine eigenmode. Supported ranks: 1 through ny. No empty slabs.
No GPU, adaptive stepping, nonlinear materials or multi-node performance claims in v0.1.
Choose heat diffusion over recovered sandpile because it offers independent analytical
checks and has no dependency on assessment source. Row slabs keep the first implementation
small; 2-D decomposition and overlap require evidence of benefit before adding complexity.

## Tasks
- [x] Write executable contract tests; observe missing executable failure.
- [x] Implement serial/MPI solver with checked input, allocation and I/O failure handling.
- [x] Validate sine eigenmode, independent impulse evolution, unequal row partitions,
      one-row slabs, 1/2/3/4 ranks, invalid arguments, output collision and bad output path.
- [x] Add reproducible benchmark harness: isolated outputs, raw repeats, hashes,
      toolchain/environment metadata, no claims from unverified or missing runs.
- [x] Document quickstart, equations, algorithm, provenance, performance limits and CI.
- [x] Run warnings, serial sanitizers, full integration suite, separate clean build;
      independent review, resolve findings, record exact tested files.

## Review focus
Integer overflow: cap dimensions and total grid cells before allocation/MPI counts.
Communication: test one-row and uneven slabs with impulse crossing rank boundaries.
Incorrect oracle: compare complete fields to independently calculated expectations.
Output safety: exclusive creation; failures abort the MPI job rather than strand ranks.
Timing: max rank loop duration; exclude initialization/output; no local-to-cluster extrapolation.

## Execution ledger
Compiler environment required explicit native Apple clang cross-targeting x86_64; see local-environment.md.
Local MPI launch required socket access. No global compiler changes were made.
Review found two benchmark-provenance defects; build manifests and saved full test logs resolve them.
Native Linux validation passed for Open MPI and MPICH, including all seven test
methods, serial sanitizers and benchmark reproduction. The owner selected MIT and
authorized publication on 6 November 2026. Native cluster performance remains
unmeasured. Current revision checks are available on the repository’s Actions page.
