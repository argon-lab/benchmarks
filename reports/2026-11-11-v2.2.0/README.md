# Argon v2.2.0 measurements, 2026-11-11

This report measures public engine tag `v2.2.0`, commit `48bd05a262d404277edefb0855ea3043d3563644`, with suite commit `5daa5d74c147975268e1110a0b8e264fe7f9ef33`. The engine source was frozen from the tag with `git archive`. A second run in the same session measures `v2.1.5`, commit `e1172b0672b797b4c528005023a5364504882a9b`, as a same-environment baseline: 2.1.6 and 2.2.0 changed history bookkeeping, checkout memory use and how history summaries are read, and this checks whether those changes moved the recorded timings.

## Workflow matrix

All **12 cells** completed for both versions: 1k/10k/50k documents × 1/4 workers × 1/4 ancestry edges, with 1,200 metadata forks, 240 sandbox/capture workflows and 20 reads per phase per cell. Divergence capture counts were exactly 500 per one-worker cell and 2,000 per four-worker cell.

Windows: v2.2.0 `2026-11-11T11:10:12.809322Z` → `2026-11-11T11:13:18.481790Z`; v2.1.5 `2026-11-11T11:13:21.903054Z` → `2026-11-11T11:16:30.210036Z`. Environment: shared Apple M6 / 24 GiB host, macOS 27.0.1 arm64, Go 1.26.11; MongoDB 7.0.45 in a Docker Desktop container (Docker Engine 29.9.3, linux/arm64 VM with 12 CPUs and about 7.7 GiB), one-member replica set `rs0`, WiredTiger 0.5 GiB cache, majority acknowledgment. Background host activity was not controlled; other containers were running on the host.

**MongoDB ran in a container here and natively in the 2026-09-24 report. The two reports are different environments and their numbers must not be compared.** Only the v2.1.5 baseline in this folder shares this environment.

- [Generated v2.2.0 report](report.md), [raw samples](raw.json), [provenance](provenance.json)
- [Generated v2.1.5 baseline report](baseline-v2.1.5/report.md), [raw samples](baseline-v2.1.5/raw.json), [provenance](baseline-v2.1.5/provenance.json)

Local checkout and output paths in the raw and provenance files were replaced with `/path/to/...` placeholders before publication; nothing else was edited.

## v2.1.5 → v2.2.0 in the same environment

Depth 4, p50 milliseconds:

| Documents | Workers | Sandbox + capture ready | Head materialize as shipped | Historical read at 50% |
|---:|---:|---|---|---|
| 1000 | 1 | 52.28 → 41.66 | 4.35 → 3.21 | 4.81 → 3.61 |
| 1000 | 4 | 52.54 → 48.50 | 5.66 → 3.75 | 6.78 → 6.12 |
| 10000 | 1 | 153.26 → 138.21 | 17.31 → 17.65 | 25.89 → 24.07 |
| 10000 | 4 | 212.07 → 220.13 | 22.61 → 21.17 | 44.96 → 47.45 |
| 50000 | 1 | 515.14 → 515.07 | 34.68 → 35.70 | 109.82 → 116.24 |
| 50000 | 4 | 1208.26 → 1277.38 | 77.03 → 73.42 | 238.59 → 233.54 |

Each version ran once, in sequence, with 20 workflow and read samples per cell. Differences of this size are within what one run on a shared host can show; this run gives **no evidence of a timing regression or a timing improvement** from 2.1.5 to 2.2.0 at these sizes. The 2.2.0 checkout change bounds peak memory by the largest collection rather than the whole branch; this suite does not measure memory, and its single-collection workload would not show that difference.

## Reproduce

```sh
GOTOOLCHAIN=go1.26.11 python3 scripts/run.py --engine /path/to/argon --ref v2.2.0 -- \
  -sizes 1000,10000,50000 -concurrency 1,4 -depths 1,4 \
  -metadata-samples 100 -workflow-samples 20 -read-samples 20 \
  -divergence-docs 100 -divergence-rounds 5 -timeout 45m
```

Repeat with `--ref v2.1.5` for the baseline. MongoDB was started with `docker run -p 127.0.0.1:27117:27017 mongo:7.0.45 --replSet rs0 --wiredTigerCacheSizeGB 0.5 --bind_ip_all` and reached through `mongodb://127.0.0.1:27117/?replicaSet=rs0&directConnection=true`.

The continuous capture and recovery experiment was not repeated for this release; the 2026-09-24 record remains the latest. The 1m-document/16-worker/16-level matrix remains unmeasured. These results do not establish multi-node failover, disk-loss recovery, large production capacity or an availability SLA.
