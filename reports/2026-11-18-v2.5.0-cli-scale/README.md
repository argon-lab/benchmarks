# Argon v2.5.0 CLI workflow at 10k, 100k and 1m documents, with v2.4.0 before it, 2026-11-18

Argon 2.5.0 computes diff and merge plans from the documents a branch changed ([argon-lab/argon#117](https://github.com/argon-lab/argon/pull/117), closing [#112](https://github.com/argon-lab/argon/issues/112)). Up to 2.4.1 it rebuilt three complete states and compared every document. This report runs the same script as the [v2.4.0 report](../2026-11-18-v2.4.0-cli-scale/README.md) on 2.5.0, and on 2.4.0 again in the same session, so the two can be read side by side. It measures Argon only.

Metric boundaries are in the [suite README](../../README.md#cli-workflow-as-the-database-grows). These are whole-command timings of the published CLI and are not comparable with the Go matrix in the older reports.

## What ran

- **2.5.0**: the executable that `npm install -g argonctl@2.5.0` installs (`bin/argon-bin`, SHA256 `c1d5729895765f6131a2e83548ebe768af5b60374f1b24072251eb277482c880`, equal to the package's checksum and to the `argon-linux-arm64` asset of release [`v2.5.0`](https://github.com/argon-lab/argon/releases/tag/v2.5.0), commit `c906ffc8cc1e37c72efa90c8f860c6342edad80f`). Window `2026-11-18T04:33:22Z` → `2026-11-18T04:39:13Z`.
- **2.4.0, this session**: the same binary as the earlier report (SHA256 `7da8a5b9…`), started 18 seconds after the 2.5.0 run ended. Window `2026-11-18T04:39:31Z` → `2026-11-18T04:52:53Z`. In [baseline-v2.4.0/](baseline-v2.4.0/report.md).
- **2.4.0, report of 02:17Z**: the figures already published in the [v2.4.0 report](../2026-11-18-v2.4.0-cli-scale/README.md), two hours earlier on the same machine. Copied into the tables below for reference.
- **Suite**: commit `082d02ef0ad7d4d2549991d97b7230b043caa586`, scripts unmodified. `cli_scale.py` is byte-identical to the one the v2.4.0 report used.
- **Environment, data and workflow**: as in the v2.4.0 report. MongoDB 7.0.45, one-member replica set, WiredTiger cache 2 GiB; Apple M6 / 24 GiB host, Docker Desktop VM with 12 CPUs and about 13.6 GiB; one collection of about 236-byte documents with the `_id` index only; five branch workflows for each of 100 and 10,000 updated documents at each size, three diffs per workflow.

Both runs completed all three sizes, and every diff and merge plan listed exactly the updated documents: 50,500 merged updates verified per size, per version.

- 2.5.0: [generated report](report.md), [raw samples](raw.json), [provenance](provenance.json), [commands and output](commands.log)
- 2.4.0 in this session: [generated report](baseline-v2.4.0/report.md), [raw samples](baseline-v2.4.0/raw.json), [provenance](baseline-v2.4.0/provenance.json), [commands and output](baseline-v2.4.0/commands.log)
- Garbage-collection case: [output](gc-case/output.txt), produced by `scripts/gc_case_docker.sh`
- [Containers and load on the host](host-load.txt) before, between and after the two runs

Nothing in these files was edited after the runs.

## Background load

The machine was not quiet, and could not be made so: other work on it starts and stops containers on its own schedule. Two unrelated MongoDB containers were idle on the Docker VM when the 2.5.0 run began. Two more started 14 seconds into it, and another container on the VM was seen using a full CPU during the 2.4.0 run's million-document tier. Host load averages were 3.9 before the 2.5.0 run, 6.4 between the runs and 7.8 after the 2.4.0 run.

So the 2.4.0 run in this session had more competition than the 2.5.0 run, and its million-document figures are higher than the ones published two hours earlier. **The comparisons in the text below use the earlier, lower 2.4.0 figures**, which makes the improvement look smaller, not larger. Each million-document tier has one run per version in this report.

## Diff and merge preview

| Step | Version and run | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---|---:|---:|---:|
| `argon diff`, 100 documents changed | 2.4.0, report of 02:17Z | 101 (85–157) | 348 (327–676) | 7,088 (4,816–14,907) |
| | 2.4.0, this session | 105 (85–123) | 545 (340–1,574) | 12,703 (6,468–17,305) |
| | **2.5.0** | **35 (20–150)** | **44 (26–463)** | **30 (22–2,150)** |
| `argon diff`, 10,000 documents changed | 2.4.0, report of 02:17Z | 179 (146–229) | 617 (421–1,203) | 8,491 (5,011–20,607) |
| | 2.4.0, this session | 163 (123–290) | 678 (501–1,066) | 10,143 (5,733–14,905) |
| | **2.5.0** | **393 (246–778)** | **450 (313–797)** | **412 (315–3,589)** |
| `argon merge preview`, 100 changed | 2.4.0, report of 02:17Z | 99 (84–104) | 351 (335–362) | 6,045 (5,141–8,425) |
| | 2.4.0, this session | 88 (85–132) | 431 (357–536) | 10,222 (7,345–15,353) |
| | **2.5.0** | **27 (25–53)** | **39 (24–82)** | **26 (23–28)** |
| `argon merge preview`, 10,000 changed | 2.4.0, report of 02:17Z | 225 (207–287) | 516 (483–693) | 6,180 (5,072–7,349) |
| | 2.4.0, this session | 181 (155–195) | 681 (560–761) | 9,358 (7,636–11,752) |
| | **2.5.0** | **386 (326–491)** | **415 (367–446)** | **385 (366–418)** |

Milliseconds, `p50 (min–max)`; 15 diffs and 5 previews per cell.

- **With 100 documents changed**, a diff and a merge preview take a few tens of milliseconds at every size. At a million documents the diff p50 went from 7,088 ms to 30 ms and the preview from 6,045 ms to 26 ms.
- **With 10,000 documents changed**, both take about 400 ms at every size: the time now follows the change. At a million documents that is 8,491 ms → 412 ms for a diff.
- **Where the branch changed every document, 2.5.0 is slower.** At 10,000 documents with all 10,000 changed, a diff went from 179 ms to 393 ms and a preview from 225 ms to 386 ms. Reading each document's history costs more per document than reading the collection once. At 100,000 documents with 10,000 changed, 2.5.0 is already ahead.
- **The first diff on each branch is much slower than the p50 says**, and for a run that diffs once it is the one that counts. See the next section.

## The first diff on a branch

Each workflow diffs three times. The first of the three is slower in both versions, and in 2.5.0 it is most of what is left:

| `argon diff`, median of 5 first diffs / median of 10 later diffs | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|
| 2.4.0 (report of 02:17Z), 100 changed | 146 / 96 | 584 / 342 | 8,269 / 5,764 |
| **2.5.0**, 100 changed | **68 / 30** | **233 / 32** | **1,874 / 28** |
| 2.4.0 (report of 02:17Z), 10,000 changed | 192 / 167 | 799 / 495 | 13,046 / 7,156 |
| **2.5.0**, 10,000 changed | **450 / 313** | **647 / 403** | **2,819 / 383** |

Milliseconds.

The cause is not the plan. In this workflow `main` is checked out and nothing is running `argon watch` on it, so a diff first brings `main`'s capture up to date by resuming a change stream on `main`'s database from where it last stopped. MongoDB serves that by scanning the oplog written since, and the oplog at that point holds the new branch's whole checkout. The MongoDB log of this run shows one such change-stream read of 1.8 to 2.4 seconds on `main`'s database for each first diff at a million documents, and none for the later ones. The garbage-collection run below does not check out `main`, and its first diff at a million documents took 29 ms.

So a first diff costs about as much as reading the oplog of the checkout that preceded it, when the parent is checked out without a watcher. Whether a running `argon watch` on the parent, or a parent managed by `argon console` or `argon mcp`, avoids it was not measured.

## What did not change

| Step | Version and run | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---|---:|---:|---:|
| New branch → first read | 2.4.0, report of 02:17Z | 96 (88–133) | 584 (535–649) | 8,472 (6,795–10,960) |
| | 2.4.0, this session | 109 (87–178) | 756 (695–1,654) | 11,495 (7,682–15,650) |
| | **2.5.0** | **135 (91–225)** | **798 (632–1,448)** | **7,534 (6,246–10,881)** |
| New sandbox → first read | 2.4.0, report of 02:17Z | 114 (102–154) | 852 (820–987) | 7,776 (6,993–8,415) |
| | 2.4.0, this session | 113 (107–160) | 808 (689–836) | 9,335 (6,755–14,474) |
| | **2.5.0** | **186 (150–206)** | **989 (746–1,135)** | **10,776 (7,700–12,771)** |
| `argon merge apply`, 100 changes | 2.4.0, report of 02:17Z | 42 (34–74) | 39 (38–240) | 112 (79–3,101) |
| | 2.4.0, this session | 54 (35–102) | 81 (52–388) | 142 (104–3,463) |
| | **2.5.0** | **46 (39–79)** | **56 (45–573)** | **55 (47–2,409)** |
| `argon merge apply`, 10,000 changes | 2.4.0, report of 02:17Z | 1,952 (1,875–2,383) | 2,164 (2,062–2,795) | 6,421 (5,499–7,814) |
| | 2.4.0, this session | 2,211 (1,904–3,290) | 2,844 (2,611–4,037) | 7,313 (6,420–9,917) |
| | **2.5.0** | **2,624 (2,315–3,234)** | **2,595 (2,282–2,857)** | **5,273 (5,181–5,755)** |
| `argon import database` | 2.4.0, report of 02:17Z | 201 (201–201) | 1,884 (1,884–1,884) | 28,377 (28,377–28,377) |
| | 2.4.0, this session | 293 (293–293) | 1,592 (1,592–1,592) | 20,631 (20,631–20,631) |
| | **2.5.0** | **263 (263–263)** | **4,065 (4,065–4,065)** | **35,094 (35,094–35,094)** |

Milliseconds, `p50 (min–max)`.

A new branch or sandbox is still a full physical copy, and `argon merge apply` still writes each change and still triggers an automatic snapshot of the target, which reads the whole branch (about 1.9 GiB at a million documents). 2.5.0 did not change these code paths; the differences between rows here are run-to-run variation on a shared machine. The import figures vary the most and have one sample each.

## Peak resident memory of one CLI process

| Command | Version and run | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---|---:|---:|---:|
| `argon diff` | 2.4.0, report of 02:17Z | 112 | 541 | 5,016 |
|  | 2.4.0, this session | 113 | 553 | 5,015 |
|  | **2.5.0** | 123 | 115 | 118 |
| `argon merge preview` | 2.4.0, report of 02:17Z | 132 | 536 | 4,860 |
|  | 2.4.0, this session | 123 | 531 | 4,923 |
|  | **2.5.0** | 120 | 114 | 121 |
| `argon merge apply` | 2.4.0, report of 02:17Z | 138 | 313 | 1,979 |
|  | 2.4.0, this session | 146 | 316 | 1,972 |
|  | **2.5.0** | 159 | 322 | 1,927 |
| `argon checkout` | 2.4.0, report of 02:17Z | 47 | 204 | 1,646 |
|  | 2.4.0, this session | 48 | 210 | 1,906 |
|  | **2.5.0** | 50 | 206 | 1,750 |

MiB, the largest value any run of that command reached, sampled every 20 ms.

`argon diff` and `argon merge preview` no longer hold the database in memory: about 120 MiB at every size, against about 5 GiB at a million documents in 2.4.0.

## After garbage collection: the parent's snapshot is read

When `argon gc` has deleted the parent's entries, 2.5.0 reads a changed document's fork-point and parent state from the parent's snapshot, loaded once per collection and side. That is a read the size of the collection. `scripts/gc_case_docker.sh` measures it: import, branch, update 100 documents, diff three times, run `argon gc --retention 0s` (which removed every entry of `main`), diff three times again.

| `argon diff`, 100 documents changed, 2.5.0 | 100,000 documents | 1,000,000 documents |
|---|---:|---:|
| Before gc, ms (three runs) | 49, 23, 17 | 29, 18, 18 |
| After gc, ms (three runs) | 207, 118, 115 | 1,551, 1,102, 1,095 |
| After gc, peak resident memory, MiB | 201–205 | 1,578–1,818 |

After gc the diff at a million documents takes about a second and 1.5 to 1.8 GiB: slower than before gc, and still several times faster than 2.4.0, with about a third of its memory. Peak memory of the before-gc diffs is not given because those processes end within one or two 20 ms samples. Three runs per cell, one collection, run once (`2026-11-18T04:53Z` onward) with two unrelated containers idle on the VM.

## Cases where 2.5.0 uses the previous algorithm (not measured)

From the engine's `docs/ARCHITECTURE.md`, "Diff and merge". None of these was measured here; in each the cost should be that of 2.4.0:

- Garbage collection has deleted entries of the branch being merged, so its log no longer names every document it changed.
- The history holds entries written before 2.1, which do not identify their document reliably.
- The branch holds more than 200,000 entries of its own.

## Other steps, 2.5.0

| Step | 10,000 documents | 100,000 documents | 1,000,000 documents |
|---|---:|---:|---:|
| Bulk update of 100 documents (ms) | 4.4 | 5.8 | 8.1 |
| Bulk update of 10,000 documents (ms) | 307 | 229 | 458 |
| Acknowledgment → 100 updates in history (ms) | 529 | 538 | 520 |
| Point read by `_id`, p50 (µs) | 85 | 73 | 102 |
| `argon branches create` (ms) | 17.8 | 31.4 | 15.3 |

## Not measured

- The three fallback cases above.
- A first diff with `argon watch` or a managed capture running on the parent.
- A second run of either version's million-document tier in this session, and a quiet machine.
- Concurrent workflows, more than one collection, larger documents, secondary indexes, conflicts, deletes, branches of branches.
- Memory of `argon watch`. DumboDB or any other system.
- The Go matrix for 2.5.0.

## Reproduce

```sh
scripts/cli_scale_docker.sh 2.5.0 results/cli-scale-2.5.0
scripts/cli_scale_docker.sh 2.4.0 results/cli-scale-2.4.0
scripts/gc_case_docker.sh 2.5.0 100000,1000000 results/gc-case.txt
```

The 2.4.0 run needs about 10 GiB of memory free in Docker for its million-document tier; the 2.5.0 run peaked lower because diff no longer holds the collection.
