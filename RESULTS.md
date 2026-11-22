# Recorded benchmark results

Every number below is scoped to its recorded engine, suite and environment. Historical measurements are retained as history; current hardening measurements are separately labelled. A dirty source snapshot is not a released engine version. See [README.md](README.md) for methodology and reproducible commands.

## 2026-11-21 · published v2.12.0: walkthrough with MongoDB Atlas as the source

Not a benchmark: a transcript of the published 2.12.0 CLI with a free MongoDB Atlas M0 (MongoDB 8.0.39) as the source and the engine on a local 7.0.45 replica set. An application thread writes to Atlas throughout. It shows the online import, following with the cluster identified by its TLS-verified Atlas hosts, a sandbox byte-identical to Atlas, four refused write-backs, a write-back in one transaction, and a write-back aborted because Atlas changed after review. [Report and transcript](reports/2026-11-21-v2.12.0-atlas-source-walkthrough/README.md).

## 2026-11-21 · published v2.10.0 and v2.11.1 alternated: what building indexes adds to a sandbox

From 2.11.0 a checkout builds each collection's recorded secondary indexes. Both releases came from npm (`argonctl@2.10.0` with binary SHA256 `3cec9b88…0747`, `argonctl@2.11.1` with `ec9a7466…d7ad`). They were run three rounds each, alternated, with `scripts/sandbox_ready_docker.sh`, at 100,000 documents of about 1 KB. **The host load average was 11 to 13 on 12 CPUs throughout; only the comparison is meaningful.**

Milliseconds until `sandbox create --watch` replies, median (min–max) of nine sandboxes:

| Fixture | 2.10.0 | 2.11.1 |
|---|---:|---:|
| 1 collection, `_id` index only | 1,980 (1,668–2,319) | 2,035 (1,727–2,346) |
| 10 collections, 20 secondary indexes | 1,700 (1,614–2,553) | 4,210 (4,053–4,273) |

Without secondary indexes the time is unchanged. Building 20 secondary indexes adds about 2.5 s at this size. [Report and raw samples](reports/2026-11-21-v2.10.0-v2.11.1-index-cost/README.md).

A transcript of what a 2.11.1 sandbox enforces (indexes, a scoped credential and its revocation) is in [reports/2026-11-21-v2.11.1-sandbox-safety](reports/2026-11-21-v2.11.1-sandbox-safety/README.md). It is not a benchmark.

## 2026-11-20 · published v2.9.0: time from `sandbox create` to the first write

This measures what an agent waits for before it can write to a new sandbox: `argon sandbox create --watch`, then a first majority-acknowledged insert on the connection string it returns. The CLI is `npm install -g argonctl@2.9.0`; the executable the launcher starts has SHA256 `c26620d7b4ca311d8affc52ee4e91f453feb54fe5485ed5b6e20176c265f0ee8`. MongoDB 7.0.45 ran as a single-member replica set with a 2 GiB cache. Documents are about 1 KB each. Window: `2026-11-21T03:24Z` → `03:38Z`. **Another session's containers shared the Docker VM throughout, and the host load average was 5 to 17 on 12 CPUs. Absolute figures are higher than on an idle machine.**

Milliseconds, median (min–max) of eight rounds:

| Fixture | Ready (forked, copied, capture running) | of which `checkout` alone | First write acknowledged | Total to first write |
|---|---:|---:|---:|---:|
| 10,000 documents, 1 collection | 217 (198–264) | 183 (166–216) | 4 (3–9) | 222 (203–271) |
| 100,000 documents, 1 collection | 2,371 (1,960–2,904) | 2,396 (2,024–3,699) | 10 (6–27) | 2,381 (1,968–2,921) |
| 1,000,000 documents, 1 collection | 16,043 (13,648–20,439) | 17,341 (12,587–20,588) | 6 (4–12) | 16,047 (13,654–20,448) |
| 100,000 documents, 10 collections | 1,386 (1,355–1,496) | 1,376 (1,264–1,589) | 5 (3–6) | 1,391 (1,358–1,501) |
| 1,000,000 documents, 10 collections | 13,059 (10,801–14,703) | 13,462 (11,031–14,648) | 7 (6–14) | 13,072 (10,807–14,709) |

Creating several at once from the same parent at 100,000 documents, ready time per sandbox:

| Sandboxes started together | Ready, each | Until all are ready |
|---|---:|---:|
| 1 | 2,240 (1,642–3,192) | 2,240 (1,642–3,192) |
| 4 | 2,578 (1,805–3,569) | 2,591 (1,825–3,571) |
| 16 | 10,906 (9,011–12,072) | 11,068 (9,139–12,073) |

- **The physical copy is almost all of the wait.** A fork takes 8–34 ms at every size. `checkout` alone takes about as long as the whole ready time, and grows with the data: about 0.2 s at 10 MB, 2.4 s at 100 MB and 16 s at 1 GB. After that the first write takes milliseconds.
- **Concurrency.** Four sandboxes at once cost about what one does. Sixteen take about five times as long each, so sixteen 100 MB sandboxes are all ready after about 11 s.
- **Capture lag.** A write became visible in Argon's history about 505 ms after its acknowledgement in every cell. That is the capture's default batching, not a cost of size.
- **Indexes.** The ten-collection fixture had a compound and a unique secondary index per collection in the source. Argon copies documents only, so the sandboxes have only `_id` indexes, as in the one-collection fixture. Why ten smaller collections copied faster than one large one was not investigated. It also means an agent's sandbox does not enforce the source's unique constraints. `argon merge check` reports such collisions before a write-back.
- **Tail latency.** Eight rounds give a median and a range, not tail latency.

[Report, raw samples, host load log and provenance](reports/2026-11-20-v2.9.0-sandbox-ready/README.md).

## 2026-11-19 · published v2.8.0: walkthrough of a followed source, from online import to write-back

Not a benchmark: a transcript of the published 2.8.0 CLI (`argonctl@2.8.0`, SHA256 `58ad3b5d4b2bc35fc8086480fddc9e89ec126c2e725fbde2b03926cebd9dbbd7`) importing a 50,200-document database online while an application thread writes to it, following it, forking sandboxes, previewing a plan and writing it back to the source with `--approve`, with the refusals and an aborted write-back. Two MongoDB 7.0.45 one-member replica sets without access control. Sandboxes held the source's values with fields in a different order, and a written-back replacement carried that order to the source. [Report and transcript](reports/2026-11-19-v2.8.0-live-source-walkthrough/README.md).

## 2026-11-18 · published v2.6.0 and v2.5.0 alternated: the first diff after a checkout

Argon 2.6.0 has a checkout keep its parent's capture position current while it copies ([argon-lab/argon#122](https://github.com/argon-lab/argon/pull/122), closing [#120](https://github.com/argon-lab/argon/issues/120)). Executables from `npm install -g argonctl@2.6.0` (SHA256 `edba0c2ecf6be346896ac0e3cc0b199515c0420a68c12a35cf2f19de12a7b113`, release [`v2.6.0`](https://github.com/argon-lab/argon/releases/tag/v2.6.0), commit `86e53d5a46084e160b3c8dd8309481f6b73372eb`) and `argonctl@2.5.0`, alternated round by round on one project with `scripts/interleaved_release_docker.sh`; window `2026-11-18T10:14Z` → `10:45Z`. **The host's load average was 10 to 16 on 12 CPUs throughout, so every absolute figure is inflated; only the comparison within a run is meaningful.**

Milliseconds, median (min–max) of six rounds, 100 documents changed, `main` checked out and unwatched:

| Step | Version | 100,000 documents | 1,000,000 documents |
|---|---|---:|---:|
| First `argon diff` on a branch | 2.5.0 | 332 (242–898) | 5,476 (2,429–8,589) |
| | 2.6.0 | 84 (43–1,313) | 173 (89–448) |
| Second `argon diff` | 2.5.0 | 68 (33–1,095) | 93 (32–102) |
| | 2.6.0 | 48 (30–115) | 110 (49–597) |
| `argon checkout` of the new branch | 2.5.0 | 1,081 (791–1,973) | 28,320 (15,847–44,373) |
| | 2.6.0 | 1,021 (803–1,337) | 38,726 (19,567–47,768) |

The first diff on a branch now costs about what a later one does. The oplog of the checkout is read during the checkout instead: over sixteen alternated rounds at 1m documents 2.6.0's checkouts took 12% longer in total, within the spread of either release, so a cost to checkout is neither shown nor excluded. With 10,000 documents changed at 1m documents, 2.6.0's later diffs and merge previews ran about twice as slow as 2.5.0's because they start sooner after the copy; with a 10-second pause in both the difference is gone. Two full `cli_scale.py` runs were made one after the other under different load and are not comparable with each other. Experimental features of 2.6.0 were not measured. Details, limits and files: [report](reports/2026-11-18-v2.6.0-cli-scale/README.md).

## 2026-11-18 · published v2.5.0 CLI at 10k/100k/1m documents, with v2.4.0 before it

Argon 2.5.0 computes diff and merge plans from the documents a branch changed ([argon-lab/argon#117](https://github.com/argon-lab/argon/pull/117)). Same script and environment as the v2.4.0 entry below: executable from `npm install -g argonctl@2.5.0` (SHA256 `c1d5729895765f6131a2e83548ebe768af5b60374f1b24072251eb277482c880`, release [`v2.5.0`](https://github.com/argon-lab/argon/releases/tag/v2.5.0), commit `c906ffc8cc1e37c72efa90c8f860c6342edad80f`); suite `082d02ef0ad7d4d2549991d97b7230b043caa586`; window `2026-11-18T04:33:22Z` → `2026-11-18T04:39:13Z`. 2.4.0 was run again straight afterwards. **The host was shared and not quiet during either run; each million-document tier has one run.** Whole-command timings, not comparable with the Go matrix.

Milliseconds, p50, 2.4.0 (entry below) → 2.5.0:

| Step | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|
| `argon diff`, 100 documents changed | 101 → 35 | 348 → 44 | 7,088 → 30 |
| `argon diff`, 10,000 documents changed | 179 → 393 | 617 → 450 | 8,491 → 412 |
| `argon merge preview`, 100 changed | 99 → 27 | 351 → 39 | 6,045 → 26 |
| `argon merge preview`, 10,000 changed | 225 → 386 | 516 → 415 | 6,180 → 385 |
| Peak resident memory of one `argon diff`, MiB | 112 → 123 | 541 → 115 | 5,016 → 118 |
| New branch → first read (unchanged code path) | 96 → 135 | 584 → 798 | 8,472 → 7,534 |
| `argon merge apply`, 100 changes (unchanged code path) | 42 → 46 | 39 → 56 | 112 → 55 |

Diff and merge preview now follow the size of the change. The p50 hides the first diff on each branch, which with `main` checked out and unwatched also catches up `main`'s capture: a median of 1,874 ms at 1m documents (8,269 ms in 2.4.0), against 28 ms for later diffs. Where a branch changed every document (10,000 of 10,000) 2.5.0 is slower than 2.4.0. A new branch or sandbox is still a full copy. After `argon gc` has deleted the parent's entries a diff reads the parent's snapshot: about 1.1 s and 1.5 to 1.8 GiB at 1m documents, measured separately. Three cases fall back to the previous algorithm and were not measured. [Tables with spreads and the same-session 2.4.0 run, the gc case, load on the host, what was not measured and reproduction](reports/2026-11-18-v2.5.0-cli-scale/README.md); [generated report](reports/2026-11-18-v2.5.0-cli-scale/report.md); [all raw samples](reports/2026-11-18-v2.5.0-cli-scale/raw.json).

---

## 2026-11-18 · published v2.4.0 CLI, whole-command timings at 10k/100k/1m documents

A different measurement from the matrices below: [`scripts/cli_scale.py`](scripts/cli_scale.py) times whole commands of the executable that `npm install -g argonctl@2.4.0` installs (SHA256 `7da8a5b960a9985bf8f4c71fa235cdc0212dc80ed9c51e1e6fea8b9350ff3cff`, release [`v2.4.0`](https://github.com/argon-lab/argon/releases/tag/v2.4.0), commit `1ad461a2ccd2dd8c7e01168f480e052f76a37f12`); suite `44cb19bde0629c8276080896a31f91448161bb44`. **Do not compare these figures with the Go matrix figures in the other entries.** Run after DoltHub published [figures for Argon at these sizes](https://www.dolthub.com/blog/2026-11-10-argon-spotlight/); Argon only, DumboDB was not run.

Environment: shared Apple M6 / 24 GiB host, macOS 27.0.1 arm64; CLI and MongoDB 7.0.45 in two containers sharing one network namespace on Docker Desktop (Engine 29.9.3, linux/arm64 VM with 12 CPUs and about 13.6 GiB), one-member replica set `rs0`, WiredTiger 2 GiB cache, majority acknowledgment. One collection of about 236-byte documents with the `_id` index only. Window: `2026-11-18T02:17:52Z` → `2026-11-18T02:28:16Z`. **Three unrelated MongoDB containers started on the same VM during the window; the whole 1m tier ran alongside them, and it has one run.** The 10k and 100k tiers were repeated.

Milliseconds, `p50 (min–max)`:

| Step | n | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|---:|
| New branch → first read | 10 | 96 (88–133) | 584 (535–649) | 8,472 (6,795–10,960) |
| New sandbox → first read | 5 | 114 (102–154) | 852 (820–987) | 7,776 (6,993–8,415) |
| `argon diff`, 100 documents changed | 15 | 101 (85–157) | 348 (327–676) | 7,088 (4,816–14,907) |
| `argon diff`, 10,000 documents changed | 15 | 179 (146–229) | 617 (421–1,203) | 8,491 (5,011–20,607) |
| `argon merge preview`, 100 changed | 5 | 99 (84–104) | 351 (335–362) | 6,045 (5,141–8,425) |
| `argon merge apply`, 100 changes | 5 | 42 (34–74) | 39 (38–240) | 112 (79–3,101) |
| `argon merge apply`, 10,000 changes | 5 | 1,952 (1,875–2,383) | 2,164 (2,062–2,795) | 6,421 (5,499–7,814) |
| `argon import database` | 1 | 201 | 1,884 | 28,377 |

A new branch or sandbox, a diff and a merge preview grow with the number of documents in the database; diff and preview cost about the same for 100 changed documents as for 10,000. One `argon diff` process peaked near 5 GiB of resident memory at 1m documents (225 MiB of BSON). Point reads by `_id` on a checked-out branch had a p50 of 78, 81 and 129 µs. [Comparison with DoltHub's published figures, memory, storage, the repeat, what was not measured and reproduction](reports/2026-11-18-v2.4.0-cli-scale/README.md); [generated report](reports/2026-11-18-v2.4.0-cli-scale/report.md); [all raw samples](reports/2026-11-18-v2.4.0-cli-scale/raw.json); [every command and its output](reports/2026-11-18-v2.4.0-cli-scale/commands.log). Five workflows per cell make the maximum the observed maximum. The Go matrix was not repeated for 2.4.0.

---

## 2026-11-11 · released v2.2.0 source, 12-cell matrix, containerized MongoDB

Engine [`v2.2.0`](https://github.com/argon-lab/argon/releases/tag/v2.2.0), commit `48bd05a262d404277edefb0855ea3043d3563644`; suite `5daa5d74c147975268e1110a0b8e264fe7f9ef33`. The engine was frozen from the tag. All 12 cells completed: 1k/10k/50k documents × 1/4 workers × 1/4 ancestry levels, with 1,200 metadata forks, 240 sandbox/capture workflows and 15,000 captured divergence records.

Environment: shared Apple M6 / 24 GiB host, macOS 27.0.1 arm64, Go 1.26.11; MongoDB 7.0.45 in a Docker Desktop container (Docker Engine 29.9.3, linux/arm64 VM with 12 CPUs and about 7.7 GiB), one-member replica set `rs0`, WiredTiger 0.5 GiB cache, majority acknowledgment. Window: `2026-11-11T11:10:12.809322Z` → `2026-11-11T11:13:18.481790Z`. Background host activity was uncontrolled. **MongoDB ran in a container, unlike the native deployment of the 2026-09-24 record below, so the two records must not be compared.**

Selected depth 4 observations, milliseconds (`p50 / p95 / p99`):

| Documents | Workers | Metadata fork (n=100) | Sandbox + capture ready (n=20) | First native query (n=20) | Ack → WAL observed (n=20) |
|---:|---:|---|---|---|---|
| 1000 | 1 | 1.99 / 3.98 / 4.50 | 41.66 / 47.17 / 50.31 | 1.85 / 2.21 / 2.51 | 504.53 / 506.58 / 506.91 |
| 1000 | 4 | 3.82 / 5.24 / 5.92 | 48.50 / 93.89 / 112.77 | 1.80 / 2.66 / 3.02 | 504.45 / 508.32 / 510.69 |
| 10000 | 1 | 3.46 / 4.62 / 4.96 | 138.21 / 155.10 / 161.82 | 1.74 / 2.77 / 3.47 | 504.74 / 508.42 / 510.32 |
| 10000 | 4 | 3.69 / 4.97 / 5.71 | 220.13 / 303.06 / 393.03 | 1.95 / 3.86 / 4.53 | 504.51 / 508.57 / 511.56 |
| 50000 | 1 | 3.52 / 6.05 / 7.54 | 515.07 / 601.54 / 608.08 | 1.79 / 2.29 / 4.01 | 506.42 / 508.83 / 522.67 |
| 50000 | 4 | 3.61 / 4.71 / 4.98 | 1277.38 / 1364.07 / 1778.08 | 2.14 / 2.68 / 7.60 | 506.50 / 508.90 / 509.59 |

A [v2.1.5 baseline](reports/2026-11-11-v2.2.0/baseline-v2.1.5/report.md) ran immediately afterwards in the same environment. One run per version shows no evidence of a timing regression or improvement between 2.1.5 and 2.2.0 at these sizes; the suite does not measure memory. [Full generated report](reports/2026-11-11-v2.2.0/report.md), [all raw samples](reports/2026-11-11-v2.2.0/raw.json), and [comparison, provenance and reproduction](reports/2026-11-11-v2.2.0/README.md). Twenty workflows per cell make p99 the observed maximum. The recovery experiment was not repeated.

---

## 2026-09-24 · released v2.1.2 source, 12-cell matrix

Engine [`v2.1.2`](https://github.com/argon-lab/argon/releases/tag/v2.1.2), commit `03559026972457ea663fdbc77d252e20ffb65b63`; suite `1e9fa82b30593beea851e2ff624eaf7d6cda0434`. Both measured trees were clean and frozen. All 12 cells completed: 1k/10k/50k documents × 1/4 workers × 1/4 ancestry levels, with 1,200 metadata forks, 240 sandbox/capture workflows and 15,000 verified captured divergence updates.

Environment: shared Apple M6 / 24 GiB host, macOS 27.0 arm64, Go 1.26.6, native MongoDB 7.0.43 one-member replica set, WiredTiger 0.5 GiB cache and majority acknowledgment. Window: `2026-09-24T07:46:20.711026Z` → `2026-09-24T07:50:05.174369Z`. Background host activity was uncontrolled; no heavy Argon test suite or timing matrix ran concurrently. This environment differs from earlier reports, so the numbers are not a controlled comparison.

Selected depth 4 observations, milliseconds (`p50 / p95 / p99`):

| Documents | Workers | Metadata fork (n=100) | Sandbox + capture ready (n=20) | First native query (n=20) | Ack → WAL observed (n=20) |
|---:|---:|---|---|---|---|
| 1000 | 1 | 15.77 / 18.16 / 18.76 | 136.75 / 154.69 / 157.05 | 11.59 / 16.21 / 18.61 | 514.47 / 518.71 / 552.94 |
| 1000 | 4 | 23.99 / 33.65 / 37.81 | 186.90 / 271.21 / 317.32 | 12.86 / 27.07 / 34.99 | 512.25 / 522.56 / 534.36 |
| 10000 | 1 | 11.01 / 17.12 / 19.26 | 231.53 / 249.21 / 255.47 | 8.77 / 10.03 / 13.08 | 510.53 / 518.88 / 522.59 |
| 10000 | 4 | 20.83 / 23.96 / 24.13 | 351.07 / 520.30 / 647.30 | 7.00 / 11.24 / 21.46 | 510.34 / 522.28 / 534.43 |
| 50000 | 1 | 16.06 / 18.94 / 18.98 | 599.11 / 646.29 / 761.98 | 5.80 / 8.15 / 9.46 | 518.62 / 522.88 / 524.57 |
| 50000 | 4 | 17.87 / 28.93 / 35.88 | 1425.89 / 1599.13 / 2122.08 | 8.46 / 20.00 / 22.29 | 510.28 / 518.61 / 524.15 |

[Full generated report](reports/2026-09-24-v2.1.2/report.md), [all raw samples](reports/2026-09-24-v2.1.2/raw.json), and [provenance/reproduction instructions](reports/2026-09-24-v2.1.2/README.md). All summary quantiles were independently recomputed from raw samples. Twenty workflows per cell make p99 the observed maximum. Sandbox readiness includes a full physical copy; metadata latency does not describe total readiness. Ack-to-observed latency includes batching and polling, and is separate from native write acknowledgment. Storage data distinguishes logical document bytes from immediate allocated collection/index bytes.

The separate published-binary recovery experiment completed 600.25 seconds with 1,865 acknowledged native writes and 1,866 exact history/state checks. Killing and restarting the API midway, with an additional write while it was stopped, recovered in 0.329 seconds; final graceful shutdown took 0.039 seconds (exit 0). [Summary](reports/2026-09-24-v2.1.2/recovery.json) and [all samples](reports/2026-09-24-v2.1.2/recovery-samples.json) are retained. This is a single-writer local correctness/soak result, not a production uptime or database failover claim.

The 1m/16-worker/16-depth expansion remains an experiment plan; production tail latency and multi-node availability are not established by this run.

---

## 2026-09-07 · committed hardening engine, Go 1.26.6

This final local matrix uses exact engine commit `ba6e06a9a3b31124d6c37475b5667dd70ab42379` and suite commit `a05950938a8eae5ba8cd089a02d9b7207a641945`. Both were frozen from clean committed sources. **This identifies a local commit build, not a tag release.** The previous dirty-source diagnostic below remains a separate historical record.

The matrix completed all 8 cells (1k/10k documents × 1/4 workers × 1/4 ancestry), with 800 metadata fork samples, 160 sandbox/capture workflows, 20 reads per phase per cell and verified divergence capture counts. Runtime was Go 1.26.6 on darwin/arm64, MongoDB 7.0.14 in one-member rs0, on the shared Apple M1 Pro / 16 GiB host. Native measured writes and engine transaction commits use majority acknowledgement. No other Argon heavy test suite ran concurrently; background host activity remains uncontrolled.

| Provenance | Value |
|---|---|
| Window UTC | 2026-09-07T08:03:37.922135Z → 2026-09-07T08:05:50.845488Z |
| Engine source SHA256 | `4d4e861c6717dcb48fa2fb64004e6b94d6c2b4c4643542c4e1165104e0d285ad` |
| Engine tracked diff SHA256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty diff) |
| Suite executable source SHA256 | `37189f5052aba444d93cdb9aa5a205dd96a49de93c555795baa560de5dca86aa` |

[Full generated report](reports/2026-09-07-committed/report.md), [all raw samples](reports/2026-09-07-committed/raw.json), [exact-ref reproduction instructions](reports/2026-09-07-committed/README.md).

Selected milliseconds (`p50 / p95 / p99`):

| Documents | Workers | Ancestry | Metadata fork (n=100) | Sandbox + capture ready (n=20) | First native query (n=20) | Ack → WAL observed (n=20) |
|---:|---:|---:|---|---|---|---|
| 1000 | 1 | 1 | 17.94 / 19.96 / 20.10 | 153.37 / 223.65 / 225.54 | 10.05 / 18.09 / 19.11 | 512.62 / 516.72 / 570.35 |
| 1000 | 1 | 4 | 19.03 / 31.17 / 32.25 | 152.43 / 173.65 / 259.78 | 9.97 / 12.66 / 28.52 | 512.42 / 516.76 / 516.80 |
| 1000 | 4 | 1 | 24.83 / 28.04 / 29.27 | 216.73 / 356.62 / 406.53 | 10.60 / 15.11 / 16.19 | 510.42 / 512.60 / 520.35 |
| 1000 | 4 | 4 | 22.98 / 26.07 / 31.28 | 210.78 / 362.46 / 431.65 | 10.93 / 18.03 / 55.00 | 508.47 / 514.43 / 534.28 |
| 10000 | 1 | 1 | 16.91 / 19.98 / 21.10 | 290.32 / 299.11 / 304.46 | 7.45 / 10.62 / 12.01 | 512.45 / 514.83 / 516.63 |
| 10000 | 1 | 4 | 16.15 / 21.05 / 23.10 | 295.69 / 429.14 / 437.89 | 10.58 / 22.94 / 23.99 | 512.50 / 514.69 / 516.66 |
| 10000 | 4 | 1 | 31.19 / 60.43 / 67.11 | 447.40 / 904.73 / 1150.88 | 14.37 / 22.20 / 23.23 | 514.40 / 522.25 / 522.33 |
| 10000 | 4 | 4 | 28.07 / 33.04 / 34.06 | 371.45 / 753.81 / 977.85 | 10.65 / 16.29 / 21.40 | 510.41 / 516.30 / 524.35 |

These small-sample tails describe this run only. Readiness includes full physical checkout and capture startup; first query separately includes connection establishment. Ack-to-WAL visibility includes a 2 ms polling interval and query overhead. Full raw output also reports import, inherited/historical materialization, explicit snapshots, all physical checkout copies and divergence storage milestones. Allocated dbStats values can lag checkpoints; compare logical data and allocated storage/index observations separately.

---

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
