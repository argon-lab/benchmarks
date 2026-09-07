# Argon workflow benchmarks

This suite measures an explicit Argon engine checkout. It distinguishes a metadata-only fork from a sandbox with a physical MongoDB copy and capture ready, then measures the first native query, captured-write visibility and storage after divergence. Every successful run writes all timing samples, nearest-rank p50/p95/p99, configuration, environment and source provenance.

The workflow runner requires the engine's `StartCapture`, `SyncBranch` and `WaitAuto` APIs. The dependency in `go.mod` is the historical published baseline, **not** the code measured by this runner. Until these APIs are released, an explicit checkout containing the hardening changes is required. `scripts/run.py` uses a temporary module replacement, freezes the exact engine source, and records its Git ref, dirty status, tracked diff SHA256, complete source manifest/hash and build module information. It also archives the frozen engine and executable suite source, including untracked files; unpublished code is labelled accordingly. The suite's executable source hash identifies runner changes before a suite commit exists.

## Run locally

Requires Go 1.26.6+, Python 3, Git and MongoDB 7+ configured as a replica set. Use an isolated database deployment. The suite creates unique `argonbench_meta_*` and `argonbench_src_*` databases plus physical sandbox databases, and removes its databases after each scenario. It never uses the normal `argon_wal` metadata database. Abrupt process termination can leave these fixture databases behind.

```sh
export MONGODB_URI='mongodb://localhost:27017/?replicaSet=rs0'
export GOCACHE=/tmp/argon-benchmark-go-cache
export GOTOOLCHAIN=go1.26.6
python3 scripts/run.py --engine /absolute/path/to/argon -- \
  -sizes 1000,10000 -concurrency 1,4 -depths 1,4 \
  -metadata-samples 100 -workflow-samples 20 -read-samples 20
```

Each run gets a fresh `results/<UTC timestamp>/` directory. Set `--results /new/output/directory` before `--` to choose it. Existing result directories are rejected. Add `--ref <exact-engine-commit>` before `--` to measure that committed tree even if the source checkout later changes. Both engine and suite source are frozen before building; later edits in the original checkouts cannot affect the measured binary. The wrapper rejects edits detected during the copy.

To run both the suite and MongoDB in containers (an explicitly selected engine is still required):

```sh
export ARGON_ENGINE_SOURCE=/absolute/path/to/argon
mkdir -p results
docker compose up --build --abort-on-container-exit --exit-code-from bench
# Removes only this Compose project's test deployment.
docker compose down
```

The Compose configuration pins MongoDB 7.0.14 and configures replica set `rs0`. Host-local and container measurements are separate environments and must not be compared as equivalent runs. The current local report was run on the host; the container recipe has not yet been exercised on this machine.

## Measurements and definitions

| Metric | Boundary |
|---|---|
| `metadata_fork_ms` | `CreateBranch` against inherited history, no physical checkout |
| `sandbox_capture_ready_ms` | Fork + full checkout + capture startup readiness acknowledgement |
| `first_native_query_ms` | New Mongo client/handshake + verified indexed `FindOne`, after readiness |
| `native_write_ack_ms` | One native `$inc` with majority write concern |
| `capture_ack_to_observed_ms` | Native acknowledgement → polling observes the committed WAL event; includes polling/query overhead |
| `native_write_to_observed_ms` | Native update start → that same visibility observation |
| `head_materialize_as_shipped_ms` | Full inherited collection read, before this suite creates an explicit snapshot |
| `head_materialize_after_snapshot_ms` | Same read after an explicit snapshot at imported main |
| `historical_25pct_ms`, `historical_50pct_ms` | Full collection replay at 25%/50% of seeded document count as a target LSN; control records also consume LSNs |
| `divergence_bulk_and_capture_ms` | Repeated native bulk updates + capture barrier, one sample per concurrent branch |

The imported data has deterministic string IDs and a 128-byte payload. `-depths` counts ancestry edges from imported main to the workload parent; it is distinct from historical replay LSN. Sandbox workflows and divergence run after the imported-main snapshot phase, so their inherited source has an explicit snapshot. Every first query must return the known document; captured point materialization must contain the new value. Divergence must capture exactly `workers × min(documents, divergence-docs) × divergence-rounds` WAL records; any mismatch fails the run.

Metadata storage observations use MongoDB `dbStats` and keep logical data, allocated collection bytes and allocated index bytes separate. Each checked-out database is measured too: a sandbox consumes a full physical copy in this architecture. Divergence records raw stored WAL BSON bytes and changed current-document BSON bytes, followed by explicit divergent snapshots. That ratio counts repeated updates in the numerator and each changed current document once in the denominator; it excludes snapshots, indexes and physical copies. It is not disk amplification. WiredTiger allocation deltas are quantized, can include retained freed pages and are not universal per-branch prices. Storage measurements currently require the MongoDB chunk backend.

All samples are retained, including first executions. There is no discarded warmup or coordinated-omission correction. A fixed worker count submits the next operation after the previous finishes (closed loop); scenarios and phases run sequentially. Concurrency is within a phase, not an externally sustained arrival rate. Small local sample counts describe that run; p99 with fewer than 100 samples is generally the maximum and does not establish production tail latency. Absolute rates depend on journal, write concern, CPU, RAM, storage and topology.

## Expanded scale/concurrency matrix

```sh
export ARGON_ENGINE_SOURCE=/absolute/path/to/argon
./scripts/expanded.sh
```

This runs 1k/50k/1m documents × 1/4/16 workers × 1/4/16 ancestry depth, with 1,000 fork, 200 workflow and 100 read samples per phase, 1,000 changed documents and 10 divergence rounds. It is resource intensive and has a 24-hour deadline. It is a runnable experiment plan, **not a claim that this matrix has been measured**. Override flags at the end to scope a run. For a quick smoke test use one size, one worker and two samples.

## Published results

See [RESULTS.md](RESULTS.md). Historical numbers retain their original date and exact scope. New results include raw samples and source hashes; no dirty working tree is identified as a released engine version. Benchmark failure exits nonzero and does not publish a complete report.
