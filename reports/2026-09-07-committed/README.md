# Committed-engine workflow matrix, 2026-09-07

Engine commit: `ba6e06a9a3b31124d6c37475b5667dd70ab42379`; suite commit: `a05950938a8eae5ba8cd089a02d9b7207a641945`. Both source trees were clean committed sources at the measured build. This is a local commit build, not a released tag. The runner used `--ref` and froze both source trees before compiling; later checkout edits cannot alter the binary.

Go: go1.26.6; MongoDB: 7.0.14. Full configuration/environment, all samples and percentile summaries are in `raw.json`; `report.md` is generated from the same run. `provenance.json` records refs, per-file manifests, aggregate source SHA256 and the actual Go module replacement/build information.

Reproduce by checking out the suite commit above and running:

```sh
GOTOOLCHAIN=go1.26.6 python3 scripts/run.py --engine /path/to/argon --ref ba6e06a9a3b31124d6c37475b5667dd70ab42379 -- \
  -sizes 1000,10000 -concurrency 1,4 -depths 1,4 \
  -metadata-samples 100 -workflow-samples 20 -read-samples 20 \
  -divergence-docs 100 -divergence-rounds 3 -timeout 30m
```

The engine clone must contain that exact commit. Use an isolated MongoDB 7+ replica set as described in the suite README. The runner archives both source trees in its local output directory; committed Git refs plus the manifests identify the measured implementation without embedding a second engine copy in this public report.

Public copies redact developer checkout/output paths and random compiler paths. The unredacted local originals remain in the run output. This report includes no measured MongoDB URI or deployment credentials. Storage sizes are immediate dbStats observations, including unflushed/retained WiredTiger allocations; they are not steady-state disk footprints. Twenty workflow samples per cell make p99 the observed maximum, not an established production tail.
