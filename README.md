# argon-benchmarks

Reproducible benchmarks for [Argon](https://github.com/argon-lab/argon), the
Git-like branching and time-travel engine for MongoDB.

**The contract:** every performance number Argon publishes — on
[argonlabs.tech](https://www.argonlabs.tech), in the README, anywhere — must
come from a run of this suite that you can reproduce yourself. No number
without a runnable source. Numbers that predate this suite were removed from
all Argon materials in July 2026.

## Run it

```bash
git clone https://github.com/argon-lab/benchmarks
cd benchmarks
docker compose up --build --abort-on-container-exit
```

The report prints to stdout and lands in `./results/report.md`, including the
exact engine commit, MongoDB version, and hardware context of the run.

Tunables (edit `docker-compose.yml` command or run the binary directly):

| flag | default | meaning |
|---|---|---|
| `-docs` | 50000 | documents seeded and imported (history size) |
| `-iters` | 200 | iterations for branch-create latency |
| `-branches` | 200 | branches created for the storage suite |
| `-depths` | 1000,10000,50000 | history depths (LSNs) for time-travel reads |

## What is measured, and how

The suite seeds a plain MongoDB database, imports it through
`walcli.ImportDatabase` (the same code path the `argon` CLI drives, which
creates the project and its WAL history), then measures through
`pkg/walcli` — the same Go services the CLI itself uses. The engine
version is pinned in `go.mod` and embedded in every report automatically.

1. **Branch creation latency** — p50/p95/p99 over `-iters` creations on a
   project that already has real history. Argon's claim is architectural:
   a branch is one metadata document, so latency must not depend on data
   size.
2. **Time-travel materialization** — latency of reconstructing collection
   state at increasing history depths, with the engine's shipped defaults
   (automatic snapshots on). The report also prints how many auto-snapshots
   existed after import, so the effect is attributable.
3. **Snapshot at head** — the same read before an explicit snapshot, the
   snapshot's creation cost, and the read after it: the bounded-replay
   effect in isolation.
4. **Materialization throughput** — documents/second derived from the head
   reads in (3).
5. **Storage cost per branch** — `dbStats` delta (data+index bytes) across
   `-branches` creations: the metadata-only claim, measured.
6. **Bulk import throughput** — wall time of `walcli.ImportDatabase` for the
   whole seeded dataset. This is the bulk-ingest path, not a per-operation
   write microbenchmark (see below).

## What is deliberately NOT measured (yet)

- **Per-operation write throughput** through the driver interceptor, and
  **storage amplification under branch divergence** — both need write access
  from an external module, which the engine does not currently export
  (`internal/driver` is not reachable through `pkg/walcli`). Tracked in
  [argon-lab/argon#16](https://github.com/argon-lab/argon/issues/16); the
  suites land here as soon as the surface exists.
- Anything involving a wire-protocol proxy or per-branch connection strings
  (that's M3).

## Methodology notes

- The engine version is pinned in `go.mod` and read from build info at
  runtime, so it appears in every report. A result without a pinned ref is
  not a result.
- Runs happen inside Docker on whatever machine you have; absolute numbers
  vary with hardware. The report always embeds the environment. Compare
  shapes and ratios (e.g. flat branch-create latency vs history size, the
  before/after-snapshot delta), not absolute values across machines.
- One warm MongoDB instance per run, fresh and empty. No connection reuse
  tricks, no cache pre-warming beyond what a real user gets.
- The suite exits non-zero on any error: a partial run never yields a report.

## Publishing rules for maintainers

Official numbers quoted by Argon come from runs recorded in
[RESULTS.md](RESULTS.md), each entry with the machine, engine ref, and the
full report. Update the website/README only by linking one of those entries.
