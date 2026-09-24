# Argon v2.1.2 measurements, 2026-09-24

This report measures public engine tag `v2.1.2`, commit `03559026972457ea663fdbc77d252e20ffb65b63`, and suite commit `1e9fa82b30593beea851e2ff624eaf7d6cda0434`. Both source trees were clean and frozen before building. The workflow matrix uses a locally compiled engine library from that exact release source; the separate recovery experiment uses the downloaded GitHub release CLI, verified against its published SHA256SUMS and release provenance.

## Workflow matrix

All **12 cells** completed: 1k/10k/50k documents × 1/4 workers × 1/4 ancestry edges. There are 1,200 metadata forks, 240 sandbox/capture workflows and 20 reads per phase per cell. Divergence capture counts were exactly 500 per one-worker cell and 2,000 per four-worker cell (15,000 total), with reconstructed values checked against acknowledged native writes. Every reported quantile was independently recomputed from the raw samples before publication.

Window: `2026-09-24T07:46:20.711026Z` → `2026-09-24T07:50:05.174369Z`. Environment: Apple M6, 24GiB RAM, 12 logical CPUs, macOS 27.0, Go go1.26.6, native MongoDB 7.0.43 in a one-member `rs0`, WiredTiger with a 0.5 GiB cache. Writes use majority acknowledgment with the journal default enabled. This is a shared developer host, with no concurrent Argon timing matrix or heavy test suite; background system load remains uncontrolled. It differs from previous report environments, so this is not a controlled speedup comparison.

- [Generated full report](report.md)
- [All raw samples/configuration/environment](raw.json)
- [Source manifests and build provenance](provenance.json)
- [Published CLI and UI provenance](release-provenance.json)

Metadata fork latency excludes physical copying. Sandbox readiness includes full checkout plus capture readiness. Capture observation includes the default batching behavior and polling overhead; it is not native write acknowledgment latency. Twenty workflow samples make p99 the observed maximum, not a reliable production tail estimate. Immediate allocated WiredTiger sizes can include retained/unflushed pages; logical document bytes, collection allocation and indexes are recorded separately. Physical sandboxes are full database copies.

## Continuous capture and API recovery

A separate **600.25-second** experiment used the published darwin/arm64 CLI (`SHA256 5688d99ea51e7bb57983cf5f44a94dded6ad79379007cea9caa7eabb2a8703c6`) on the same local MongoDB fixture. It acknowledged **1,865 native writes** (the initial insert plus 1,864 updates), checked **1,866 capture barriers**, and verified the exact WAL count and reconstructed document value after every barrier. At the halfway point the harness killed its own API process, wrote while the API was stopped, restarted it and verified catch-up in **0.329 seconds** from process start through the state/history check. Final graceful shutdown took **0.039 seconds**, exit 0. All disposable databases were cleaned up.

- [Recovery summary](recovery.json)
- [Every recovery sample](recovery-samples.json)

The writer issues one acknowledged update at a time with a 250 ms pause and verifies capture before proceeding. This is a bounded correctness/soak experiment, not throughput testing, long-term production uptime, MongoDB failover or disk-loss recovery. The final duplicate-value barrier is an intentional final verification; hence there is one more barrier than native writes.

## Reproduce

Use the recorded suite commit and a public engine checkout containing `v2.1.2`:

```sh
GOTOOLCHAIN=go1.26.6 python3 scripts/run.py --engine /path/to/argon --ref v2.1.2 -- \
  -sizes 1000,10000,50000 -concurrency 1,4 -depths 1,4 \
  -metadata-samples 100 -workflow-samples 20 -read-samples 20 \
  -divergence-docs 100 -divergence-rounds 5 -timeout 45m
```

Run the recovery experiment with the checksum-verified release binary in a separate output directory:

```sh
python3 scripts/capture_recovery.py --binary /path/to/argon-darwin-arm64 \
  --version 2.1.2 --duration-seconds 600 --output /path/to/new-recovery-output
```

Use an isolated MongoDB 7+ replica set as described in the suite README. The exact source archives are retained in the original local output; public Git refs and complete file manifests identify those sources without duplicating the engine in this report. Public JSON only replaces checkout/output/compiler temporary paths with labelled placeholders. No sample, quantile, source hash or binary hash was changed. The report includes no MongoDB URI or credentials.

The planned 1m-document/16-worker/16-level matrix remains unmeasured. These results do not establish multi-node failover, disk-loss recovery, large production capacity or an availability SLA.
