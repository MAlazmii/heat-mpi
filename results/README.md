# Recorded evidence

`clean-build-validation.txt` records a build, full suite and serial sanitizer checks
in a separate temporary directory. Local benchmark folders are deliberately ignored
by Git because their metadata contains machine-specific paths. They remain saved on
the owner's computer. Review/redact paths before selecting results for public release.

`local-final-2026-11-06/benchmark.json` and `validation.txt` contain the final run's
raw repetitions, exact commands, test log and build/source/executable fingerprints.
The host is Apple M1; both benchmark executables target x86_64 and run under translation.
Results are local smoke/performance-methodology evidence, not cluster scaling claims.

`linux-validation-summary.json` records verified native Linux jobs and tested revisions.
Full GitHub artifacts are saved locally under ignored `ci/` directories. They include
test/sanitizer logs, environment information, build manifests and repeated timings.
They establish single-host correctness/reproducibility, not multi-node scaling.
