# Contributing

Keep numerical changes small enough to review. Explain the intended mathematical
behavior, give a reproducer for fixes, and run `make CC=mpicc test` and
`make CC=gcc sanitize` before submitting. Do not silently relax a tolerance to
make a failing result pass. Changes to the method need updated reference tests
and a discussion of accuracy/stability as well as timing.

Use a matched native compiler and MPI runtime. Open MPI and MPICH are both targeted
by the Ubuntu workflow; its observed results, not merely its configuration, establish
validation. `MPIEXEC=mpiexec.mpich make CC=mpicc.mpich MPICC=mpicc.mpich test` selects
MPICH explicitly. Run `make clean` when changing compilers or build flags.

Record benchmarks with `scripts/benchmark.py` in a new directory. Preserve failed
or anomalous runs when investigating behavior; do not present selected best timings
as representative. Do not add coursework archives, private records, credentials,
large binaries or datasets. There is no required coverage percentage: prioritize
tests that detect realistic numerical or communication faults.
