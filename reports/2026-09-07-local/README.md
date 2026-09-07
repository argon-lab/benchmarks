# 2026-09-07 local diagnostic record

This completed run measured the frozen **unpublished working tree** recorded in `provenance.json`, based on engine `f87c88e5609cb54df5f630780019fcad7715e98e`. It does not identify the final hardening release. The exact binary used the recorded module replacement; the historical version printed in the module requirement does not name the modified implementation.

- `raw.json`: every measured latency and storage observation, nearest-rank summaries, configuration and provenance.
- `report.md`: human-readable report generated from the same run.
- `provenance.json`: environment-independent source fingerprints, Git base refs, dirty state and build module information; machine/Mongo environment is in `raw.json`.
- `engine.patch` + `engine-untracked.tar.gz`: tracked diff and newly created files, relative to the engine base ref.
- `suite.patch` + `suite-untracked.tar.gz`: exact runner changes relative to suite base `14b11f49177410cd3f1c0800b3e17f5957fb2e82`.
- `performance-{baseline,current}.log`: separate same-host old/new canary workloads; not samples in the workflow matrix.
- `performance-current-provenance.json`: fingerprint for that separate current-code comparison.

To reconstruct the measured sources, check out the two base refs into disposable clones, apply each repository's patch, and extract its untracked-file archive at that repository root. Hash each file against the corresponding manifest before running. Run `python3 scripts/run.py --engine /path/to/reconstructed/argon` with the matrix flags in `raw.json`/`provenance.json`. These patches preserve the measured pre-commit code even when the branches advance. Extract only these trusted local source archives into disposable checkouts.

Storage uses immediate `dbStats` observations. WiredTiger allocated size may lag dirty in-memory pages until a checkpoint and may retain freed pages. In particular, a just-created checkout can report only a few allocated pages while its logical data contains the full copied collection. These are not stable disk-footprint measurements.

The separate canary comparison changed only WAL append sample count from 10,000 to 1,000 in both disposable source copies, to compare equal sample counts. Branch creation used 100 samples; sequential and concurrent puts used 1,000 each, with 10 goroutines sharing one writer for the concurrent case. The baseline's original hardware-dependent thresholds failed; current correctness checks passed with absolute thresholds recorded rather than enforced. There was no simultaneous matrix load. No repeated-run confidence interval is claimed.

Public copies redact the developer checkout/output paths and random temporary compiler paths. The local unredacted originals remain under `results/20260907-local-matrix/`. Source hashes, versions, flags and every measured sample are unchanged. Connection strings with `user:pw` or `service:secret` inside source fixtures are synthetic unit-test cases, not measured deployment credentials. The actual measurement URI contains no credentials and is not stored in this bundle.
