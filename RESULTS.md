# Recorded benchmark results

Every number below is scoped to its recorded engine, suite and environment. Historical measurements are retained as history; current hardening measurements are separately labelled. A dirty source snapshot is not a released engine version. See [README.md](README.md) for methodology and reproducible commands.

## 2026-09-07 · local hardening diagnostic (unpublished source)

The 8-scenario matrix completed in **134.7 seconds**, with 800 metadata forks, 160 sandbox/capture workflows and verified divergent capture counts. It used 1k/10k documents × 1/4 workers × 1/4 ancestry edges. Each cell has 100 metadata samples, 20 workflow samples and 20 reads per phase. Divergence used 100 changed documents per branch over three update rounds.

| Provenance | Value |
|---|---|
| Machine | Apple M1 Pro, 8 logical CPUs, 16 GiB RAM, macOS 26.6.2; shared developer host |
| Runtime | Go 1.26.4, darwin/arm64, GOMAXPROCS=8 |
| MongoDB | 7.0.14, WiredTiger, one-member rs0, majority journal default enabled |
| Engine base | `f87c88e5609cb54df5f630780019fcad7715e98e` plus unpublished changes |
| Engine tracked diff SHA256 | `e17277de483187226ff1062b09c7c3a542f75b12917ff6c0f6fff49212083ce5` |
| Engine complete source SHA256 | `21ab9cd0a2041d93272fd3479b4b25599e7eea28b9795ffcc4771a296b482b78` |
| Suite base | `14b11f49177410cd3f1c0800b3e17f5957fb2e82` plus unpublished changes |
| Suite executable source SHA256 | `c962ff29fe311efb98c8b7e0e50b0819139b12af86bac323f5e8a6bad366c61e` |
| Measurement window | 2026-09-07 07:25:15–07:27:30 UTC |

[Full report](reports/2026-09-07-local/report.md), [raw samples](reports/2026-09-07-local/raw.json), and [provenance/reconstruction bundle](reports/2026-09-07-local/README.md). These identify the exact frozen build, not the final hardening commit or any future tag.

Selected workflow distributions, in milliseconds (`p50 / p95 / p99`):

| Documents | Workers | Ancestry | Metadata fork (n=100) | Sandbox + capture ready (n=20) | First native query (n=20) | Ack → WAL observed (n=20) |
|---:|---:|---:|---|---|---|---|
| 1000 | 1 | 1 | 19.16 / 24.42 / 28.73 | 154.40 / 181.65 / 211.76 | 10.76 / 13.67 / 14.04 | 512.79 / 516.81 / 518.43 |
| 1000 | 1 | 4 | 16.00 / 21.21 / 24.54 | 165.29 / 182.81 / 183.01 | 10.83 / 12.40 / 14.06 | 514.43 / 520.90 / 522.67 |
| 1000 | 4 | 1 | 26.07 / 31.98 / 33.25 | 233.86 / 387.24 / 452.18 | 10.65 / 20.16 / 27.95 | 510.35 / 532.31 / 534.65 |
| 1000 | 4 | 4 | 51.19 / 63.26 / 97.93 | 251.81 / 494.59 / 566.51 | 11.48 / 16.03 / 19.14 | 512.40 / 524.32 / 524.35 |
| 10000 | 1 | 1 | 19.97 / 31.38 / 35.03 | 305.53 / 324.37 / 324.54 | 8.53 / 10.98 / 13.50 | 514.62 / 520.58 / 520.73 |
| 10000 | 1 | 4 | 19.06 / 24.63 / 25.86 | 303.46 / 329.05 / 405.21 | 8.95 / 14.18 / 20.78 | 514.40 / 544.44 / 546.31 |
| 10000 | 4 | 1 | 46.77 / 63.86 / 68.88 | 389.44 / 1144.67 / 1529.79 | 12.63 / 17.48 / 28.16 | 512.25 / 528.27 / 574.35 |
| 10000 | 4 | 4 | 25.14 / 28.97 / 31.12 | 344.90 / 753.22 / 974.28 | 13.03 / 16.02 / 19.33 | 516.37 / 532.18 / 534.24 |

With n=20, p99 is the observed maximum and does not establish production tail latency. Sandbox readiness includes copying data and starting capture; first native query separately includes connection/handshake. Capture lag is observed after majority acknowledgement and includes the 2 ms polling loop. The roughly half-second low-volume lag reflects the default capture batching behavior; it must not be presented as native write acknowledgement latency.

The imported main branch already had an automatic snapshot in every cell. The suite then explicitly snapshotted imported main before sandbox workflows. Metadata forks added 48,680 logical bytes across 100 forks in each cell (486.8 logical bytes/fork in this workload, including audit metadata). This is **not a disk-cost claim**. Physical checkout logical data was 233,390 bytes at 1k documents and 2,343,890 bytes at 10k: these sandboxes contain full physical copies. Immediate allocated sizes can lag a WiredTiger checkpoint; the raw report retains them separately without treating them as settled footprints.

Divergence captured exactly 300 records with one worker and 1,200 with four. Stored WAL BSON was 244,140 / 976,560 bytes over 23,240 / 92,960 bytes of changed current-document BSON: 10.51× for three rounds of updates in this workload. This denominator counts each changed current document once; the ratio includes repeated history and excludes snapshots, indexes and physical copies. It is not total disk amplification.

### Separate old/current correctness-canary comparison

The unchanged baseline failed all four historical absolute floors on this same MongoDB fixture. The comparison below has one run per implementation, equal sample counts and no concurrent workflow matrix. It is diagnostic, not a statistical speedup/regression claim.

| Workload | Baseline f87c88e | Hardening working tree | Original absolute floor |
|---|---:|---:|---:|
| Sequential WAL append, n=1,000 | 89.55 ops/s | 81.27 ops/s | >150 ops/s |
| Metadata branch create, n=100 | 15.77 ms/op | 20.19 ms/op | <10 ms/op |
| Sequential Put, n=1,000 | 56.26 ops/s | 72.73 ops/s | >100 ops/s |
| Concurrent Put, 10 goroutines sharing one writer, n=1,000 | 377.44 ops/s | 71.61 ops/s | >500 ops/s |

**The shared-writer concurrent throughput fell by about 81% in this comparison.** The new writer serializes publication to a branch and commits WAL/pre-images/head atomically. The previous concurrency number came from uncoordinated publication with weaker correctness. The cost is real; batching and independent-branch throughput need further optimization and measurement. A correctness fix does not justify advertising the old concurrency number for the new path.

Core tests now retain workload timing and require complete acknowledged history, unique LSNs and correct published heads. The original machine-dependent limits are unchanged and explicitly enforced with `ARGON_PERF_ASSERT=1` on a calibrated performance runner. They are not silently lowered to make correctness CI pass. [Baseline log](reports/2026-09-07-local/performance-baseline.log), [current log](reports/2026-09-07-local/performance-current.log).

---

Historical scope note: the July record below predates the current capture and transaction changes. Its 479-byte value mixes logical data with allocated index delta; it is retained verbatim as a historical observation, not a universal disk price. The original record did not include raw samples or an exact suite commit, so its reproducibility is more limited than the new bundle. Current Compose defaults do not recreate its engine automatically.

## 2026-07-07 · historical first run

| | |
|---|---|
| machine | MacBook (Apple Silicon), Docker Desktop 29.6.1, linux/arm64 container, 8 CPUs |
| engine | `github.com/argon-lab/argon v1.0.2-0.20260707043331-8bf0f1e9dd85` (master @ `8bf0f1e`) |
| mongodb | 7.0.25 (container, fresh instance) |
| workload | 50,000 documents seeded and imported → head LSN 50,002; defaults for all flags |

### Headline numbers

- **Branch creation: 0.86 ms p50 / 1.93 ms p99** (n=200, on a project with a 50k-entry history)
- **Storage cost per branch: 479 bytes** (data+index delta across 200 branches — branches are metadata)
- **Bulk import: 48,287 docs/second** through `walcli.ImportDatabase`
- **Time-travel materialization: 9.5 ms at LSN 1,000 · 63.4 ms at 10,000 · 296.8 ms at 50,000** (full replay — no snapshots existed after import)
- **Snapshot at head: 295.3 ms read before → 209.3 ms after** (snapshot creation itself: 481.2 ms)

### Observations in that historical build

- Replay latency grows linearly with depth in this run because **the import
  path did not trigger automatic snapshots** (0 existed after import) —
  auto-snapshotting then hooked the driver write path only. Filed
  upstream as a finding.
- With a snapshot at head, the read is bounded by **snapshot load cost**
  (chunk decompression + BSON decode of the full collection), which is why
  the improvement at this scale is ~30% rather than dramatic. The snapshot
  win grows with replay depth avoided, not collection size.

### Full report

```
| environment | value |
|---|---|
| date (UTC) | 2026-07-07 04:47 |
| engine ref | v1.0.2-0.20260707043331-8bf0f1e9dd85 |
| go | go1.24.13 linux/arm64, 8 CPUs |
| mongodb | 7.0.25 |
| history seeded | 50000 documents → head LSN 50002 |
| auto-snapshots after import | 0 |

1 · Branch creation latency (n=200, 50002-entry history)
  p50 0.86 ms · p95 1.32 ms · p99 1.93 ms · max 7.23 ms

2 · Time-travel materialization (as-shipped configuration)
  LSN 1000  →   998 docs ·   9.50 ms
  LSN 10000 →  9998 docs ·  63.38 ms
  LSN 50000 → 49998 docs · 296.84 ms

3 · Snapshot at head (bounded replay)
  read before 295.34 ms · snapshot creation 481.19 ms · read after 209.34 ms

4 · Materialization throughput
  before snapshot 169,295 docs/s · after snapshot 238,842 docs/s

5 · Storage cost per branch (n=200)
  479 B per branch (data+index)

6 · Bulk import throughput (walcli.ImportDatabase)
  50000 docs · 1.0 s · 48,287 docs/s
```
