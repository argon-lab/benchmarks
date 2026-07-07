# Official results

Runs recorded here are the only source for performance numbers quoted in
Argon materials. Each entry pins the engine ref, the suite commit, and the
machine. Reproduce any of them with `docker compose up --build`.

---

## 2026-07-07 · first official run

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

### Honest observations

- Replay latency grows linearly with depth in this run because **the import
  path did not trigger automatic snapshots** (0 existed after import) —
  auto-snapshotting currently hooks the driver write path only. Filed
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
