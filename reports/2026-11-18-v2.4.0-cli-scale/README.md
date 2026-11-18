# Argon v2.4.0 CLI workflow at 10k, 100k and 1m documents, 2026-11-18

This report times the published Argon 2.4.0 command line, one whole command at a time, as the imported database grows from 10,000 to 100,000 to 1,000,000 documents. It was run after DoltHub published [a comparison of Argon and DumboDB](https://www.dolthub.com/blog/2026-11-10-argon-spotlight/) with figures for a new branch, diff and merge at those three sizes; until now this repository's largest measured size was 50,000 documents. It measures **Argon only**. DumboDB was not run here.

It uses a new script, `scripts/cli_scale.py`, started by `scripts/cli_scale_docker.sh`. The boundaries of every metric are in the [suite README](../../README.md#cli-workflow-as-the-database-grows). **This is a different measurement from the Go matrix in the earlier reports**, which calls the engine as a library inside one process, and the two must not be compared.

## What ran

- **Engine**: the executable that `npm install -g argonctl@2.4.0` installs (`bin/argon-bin`, SHA256 `7da8a5b960a9985bf8f4c71fa235cdc0212dc80ed9c51e1e6fea8b9350ff3cff`, equal to the package's own checksum and to the `argon-linux-arm64` asset of release [`v2.4.0`](https://github.com/argon-lab/argon/releases/tag/v2.4.0), commit `1ad461a2ccd2dd8c7e01168f480e052f76a37f12`). The binary was run directly, so the npm launcher's Node start-up is in no timing.
- **Suite**: commit `44cb19bde0629c8276080896a31f91448161bb44`, scripts unmodified; their hashes are in [provenance.json](provenance.json).
- **MongoDB**: 7.0.45 (`mongo:7.0.45@sha256:c53852c0…`), one-member replica set `rs0`, WiredTiger cache 2 GiB, majority acknowledgment for seeded and measured writes.
- **Environment**: Apple M6 / 24 GiB host, macOS 27.0.1 arm64, Docker Desktop (Engine 29.9.3, linux/arm64 VM with 12 CPUs and about 13.6 GiB). The CLI ran in a `node:24-bookworm` container that shares the MongoDB container's network namespace, so MongoDB was reached at `localhost` with no published port.
- **Data**: one collection, `items`, with a string `_id`, four small fields and a 128-byte payload, about 236 bytes of BSON per document, and the `_id` index only. `main` was checked out before the branch workflows.
- **Workflow**, five times for each of 100 and 10,000 updated documents at each size: `argon branches create`, `argon checkout`, a first read, `argon watch`, one bulk update through PyMongo, wait until Argon's history holds every update, `argon diff` three times, `argon merge preview`, `argon merge apply`, `argon release`. Then `argon sandbox create` to a first read five times, and 1,000 point reads by `_id`.
- **Window**: `2026-11-18T02:17:52Z` → `2026-11-18T02:28:16Z` (the evening of November 17 in New York).

The run fails unless every diff and merge plan lists exactly the updated documents, every merge is found in the checked-out `main`, and `main` ends with every document and the expected total of updates. All three sizes completed: 50,500 merged updates verified at each.

- [Generated report](report.md), [raw samples](raw.json), [provenance](provenance.json), [every command and its output](commands.log) (outputs longer than 4,000 characters are shortened in the middle)
- Repeat of the two smaller sizes: [report](repeat-10k-100k/report.md), [raw samples](repeat-10k-100k/raw.json), [provenance](repeat-10k-100k/provenance.json), [commands](repeat-10k-100k/commands.log)

Nothing in these files was edited after the run. After it, the wrapper `cli_scale_docker.sh` was changed only so that a host without `git` or `npm` can run it; `cli_scale.py`, which does the measuring, is as recorded.

## Background load during the run

The host was shared and its load was not controlled. Three other MongoDB containers from unrelated work were started on the same Docker VM during the window, one at `02:19:06Z` and two at `02:21:16Z`. The 10,000 tier and most of the 100,000 tier finished before the first of them; **the whole 1,000,000 tier ran alongside them.** The spread between the minimum and maximum at that size is wide, and the minimum is the figure least affected.

A second full run was started and stopped before its 1,000,000 tier, because another container on the VM was by then using about 3 GiB and the tier had needed roughly 9 GiB for the CLI and MongoDB together in the first run (read from `docker stats`, not recorded). The two smaller sizes were then repeated on their own (`02:30:33Z` → `02:31:48Z`). **The 1,000,000 tier has one run.**

## Results

### Steps that grow with the number of documents in the database

| Step | n per size | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|---:|
| New branch → first read (`new_branch_to_first_read_ms`) | 10 | 96 (88–133) | 584 (535–649) | 8,472 (6,795–10,960) |
| of which `argon checkout` (`checkout_ms`) | 10 | 78 (71–85) | 568 (520–612) | 8,411 (6,763–10,892) |
| New sandbox → first read (`sandbox_create_to_first_read_ms`) | 5 | 114 (102–154) | 852 (820–987) | 7,776 (6,993–8,415) |
| `argon diff`, 100 documents changed | 15 | 101 (85–157) | 348 (327–676) | 7,088 (4,816–14,907) |
| `argon diff`, 10,000 documents changed | 15 | 179 (146–229) | 617 (421–1,203) | 8,491 (5,011–20,607) |
| `argon merge preview`, 100 changed | 5 | 99 (84–104) | 351 (335–362) | 6,045 (5,141–8,425) |
| `argon merge preview`, 10,000 changed | 5 | 225 (207–287) | 516 (483–693) | 6,180 (5,072–7,349) |
| `argon import database` (`import_ms`) | 1 | 201 (201–201) | 1,884 (1,884–1,884) | 28,377 (28,377–28,377) |
| Driver insert of the source data (`seed_native_insert_ms`) | 1 | 44 (44–44) | 397 (397–397) | 6,095 (6,095–6,095) |

Milliseconds, `p50 (min–max)`.

`argon diff` and `argon merge preview` cost about the same whether 100 or 10,000 documents changed. Both rebuild the fork point, the branch and its parent in full and compare every document. The first diff on a branch was usually the slowest of its three; all are kept.

### Steps that follow the size of the change, or are MongoDB's own

| Step | n per size | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|---:|
| `argon branches create` (`branch_create_ms`) | 10 | 14.9 (12.0–44.5) | 15.7 (12.8–38.4) | 21.4 (14.4–57.7) |
| `argon merge apply`, 100 changes | 5 | 42 (34–74) | 39 (38–240) | 112 (79–3,101) |
| `argon merge apply`, 10,000 changes | 5 | 1,952 (1,875–2,383) | 2,164 (2,062–2,795) | 6,421 (5,499–7,814) |
| Bulk update of 100 documents on the branch | 5 | 3.0 (2.6–3.7) | 3.3 (2.7–4.0) | 7.2 (6.7–11.5) |
| Bulk update of 10,000 documents on the branch | 5 | 151 (142–216) | 168 (158–319) | 820 (425–1,115) |
| Acknowledgment → 100 updates in history | 5 | 524 (520–539) | 537 (516–538) | 520 (514–529) |
| Acknowledgment → 10,000 updates in history | 5 | 283 (257–305) | 335 (290–382) | 528 (313–763) |
| New client's first `find_one` on the branch | 10 | 1.6 (1.4–3.1) | 1.7 (1.5–4.2) | 5.6 (3.0–14.6) |

Milliseconds, `p50 (min–max)`.

`argon merge apply` writes the saved plan and does not recompute it. Every 10,000-change apply, and the fifth 100-change apply at each size, took longer and used far more memory than the other 100-change applies (at 1,000,000 documents: about 1.9 GiB against 27 MiB). That fits the engine's automatic snapshot of the target branch, which it takes roughly every 1,000 entries and which reads the whole branch. It was not traced further.

The half second between acknowledgment and history for 100 updates is `argon watch`'s batching interval, the same delay the Go matrix records as acknowledgment-to-observed.

### Point reads by `_id`

| | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|
| p50 | 78 | 81 | 129 |
| p95 | 96 | 112 | 262 |
| max | 138 | 265 | 7,017 |

Microseconds, 1,000 reads per size over one warm connection.

### Peak resident memory of one CLI process

| Command | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|
| `argon diff` | 112 | 541 | 5,016 |
| `argon merge preview` | 132 | 536 | 4,860 |
| `argon merge apply` | 138 | 313 | 1,979 |
| `argon checkout` | 47 | 204 | 1,646 |
| `argon sandbox create` | 49 | 202 | 1,772 |
| `argon import database` | 54 | 293 | 2,300 |

MiB, the largest value any run of that command reached. Sampled every 20 ms from the kernel's high-water mark, so a spike in a command's last 20 ms can be missed. `argon watch` was not sampled.

Diff and merge preview hold three complete states in memory. At 1,000,000 documents, which is 225 MiB of BSON, one `argon diff` process peaked near 5 GiB.

### Logical data size

| Database | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|
| Source database | 2.2 | 22.4 | 225.4 |
| One checked-out branch | 2.2 | 22.4 | 225.4 |
| Argon metadata after import | 4.8 | 47.8 | 479.0 |
| Argon metadata at the end of the run | 74.0 | 120.1 | 577.0 |

MiB of BSON (`dbStats.dataSize`). Every checked-out branch is a full copy of the data. Allocated bytes are in the generated report; they were read right after the writes, before WiredTiger had necessarily flushed them, and are a lower bound.

### Repeat of the 10,000 and 100,000 tiers

| Step | 10,000: first run → repeat | 100,000: first run → repeat |
|---|---:|---:|
| New branch → first read | 96 → 96 | 584 → 606 |
| New sandbox → first read | 114 → 99 | 852 → 601 |
| `argon diff`, 100 changed | 101 → 90 | 348 → 370 |
| `argon diff`, 10,000 changed | 179 → 145 | 617 → 473 |
| `argon merge preview`, 100 changed | 99 → 89 | 351 → 367 |
| `argon merge apply`, 10,000 changes | 1,952 → 1,816 | 2,164 → 2,134 |
| `argon import database` | 201 → 209 | 1,884 → 1,567 |

Milliseconds, p50. The repeat agrees with the first run to within about a quarter, except the 100,000-document sandbox step, which in the first run coincided with the first unrelated container starting.

## Beside the numbers DoltHub published for Argon

DoltHub's article gives figures for Argon without the machine, document shape, changed-document count or method, so this is not a controlled comparison and the rows may not measure the same boundary. Their figures are quoted from the article as read on 2026-11-17.

| Step in their article | Documents | Their figure for Argon | This run, p50 | Measured here as |
|---|---|---:|---:|---|
| New branch to first read | 10k / 100k / 1M | 500 / 4,000 / 47,200 ms | 96 / 584 / 8,472 ms | `new_branch_to_first_read_ms` |
| Diff | 10k / 100k / 1M | 500 / 2,200 / 23,700 ms | 101 / 348 / 7,088 ms | `diff_100_changed_ms` |
| Merge | 10k / 100k / 1M | 500 / 2,300 / 24,100 ms | 142 / 393 / 6,134 ms | `merge_preview_plus_apply_100_changed_ms` |
| 100 bulk updates on a branch | 100k | 25 ms | 3.3 ms | `bulk_update_100_ms` |
| 10,000 bulk updates on a branch | 100k | 2.2 s | 0.17 s | `bulk_update_10000_ms` |
| Point read by `_id` | 1M | 344 µs | 129 µs | `point_read_by_id_us` |
| Initial load | 1M | 230 s | 34.5 s | `seed_native_insert_ms` + `import_ms` |

For a new branch, diff and merge, this run's figures are between about 3 and 7 times lower than theirs at each size, and they grow the same way: with the number of documents. This run cannot say why the absolute figures differ.

For the same three steps their article reports DumboDB at 3 to 5 ms at every size. Those are DoltHub's measurements of their own product. Nothing here confirms or disputes them.

## Not measured

- DumboDB, or any system other than Argon.
- The 1,000,000 tier a second time, and any size above it.
- The Go matrix for 2.4.0. `sandbox_capture_ready_ms` from the earlier reports was not extended to these sizes; `sandbox_create_to_first_read_ms` here is a CLI-level measurement of a similar step, not the same metric.
- Concurrent workflows, more than one collection, larger documents, secondary indexes, branches of branches, conflicts, and deletes. Every change was an update to an existing document.
- Memory of `argon watch`; storage after WiredTiger checkpoints; MongoDB running natively; multi-node replica sets.
- Tail latency. Five workflows per cell show how a step grows; the maximum is the observed maximum.

## Reproduce

```sh
scripts/cli_scale_docker.sh 2.4.0 results/cli-scale \
  --sizes 10000,100000,1000000 --update-sizes 100,10000 \
  --samples 5 --diff-repeats 3 --point-reads 1000
```

These are the script's defaults apart from the version and output directory. It needs Docker with about 10 GiB of memory free for the 1,000,000 tier, and took a little over ten minutes here.
