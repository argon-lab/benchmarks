# Argon v2.6.0 and v2.5.0 alternated on one project: the first diff after a checkout, 2026-11-18

In Argon 2.5.0 the first `argon diff` or `argon merge preview` on a new branch took seconds at a million documents when the parent was checked out and nothing was watching it ([argon-lab/argon#120](https://github.com/argon-lab/argon/issues/120), measured in the [v2.5.0 report](../2026-11-18-v2.5.0-cli-scale/README.md#the-first-diff-on-a-branch)). Argon 2.6.0 has a checkout keep its parent's capture position current while it copies ([argon-lab/argon#122](https://github.com/argon-lab/argon/pull/122)). This report measures that change on the published 2.6.0. It measures Argon only.

**The machine was busy throughout.** Other work on it kept the host's load average between 10 and 16 on 12 CPUs for the whole session, and a 15-minute wait for a quieter moment did not find one. Every absolute figure here is higher than on a quiet machine: 2.5.0 took two to four times as long as in its own report five hours earlier. For that reason the comparison rests on runs that **alternate the two releases on one project**, so both see the same load, and not on the two full runs of `cli_scale.py`, which ran one after the other under different load.

## What ran

- **2.6.0**: the executable that `npm install -g argonctl@2.6.0` installs (`bin/argon-bin`, SHA256 `edba0c2ecf6be346896ac0e3cc0b199515c0420a68c12a35cf2f19de12a7b113`, equal to the package's checksum and to the `argon-linux-arm64` asset of release [`v2.6.0`](https://github.com/argon-lab/argon/releases/tag/v2.6.0), commit `86e53d5a46084e160b3c8dd8309481f6b73372eb`).
- **2.5.0**: the same binary as the v2.5.0 report (SHA256 `c1d5729895765f6131a2e83548ebe768af5b60374f1b24072251eb277482c880`).
- **Alternated runs** (`scripts/interleaved_release_docker.sh`, `scripts/interleaved.py`), `2026-11-18T10:14Z` to `10:45Z`. One database is seeded and imported, `main` is checked out and nothing watches it. Then, for each round and each release in turn: create a branch from `main`, check it out, update documents through the driver with that release's `argon watch` capturing, run `argon diff` twice and `argon merge preview` once, release and delete the branch. The order of the two releases is swapped every round. Every diff is checked to list exactly the updated documents.
- **Full runs** of `scripts/cli_scale_docker.sh`, unmodified, suite commit `ba305fcff9f9bf2f0cf9596e200468bc670185d2`: 2.6.0 `09:31:22Z` → `09:56:17Z`, then 2.5.0 `09:56:42Z` → `10:12:20Z`. Both completed all three sizes and verified 50,500 merged updates per size.
- **Environment**: as in the v2.5.0 report. MongoDB 7.0.45, one-member replica set, WiredTiger cache 2 GiB; Apple M6 / 24 GiB host, Docker Desktop VM with 12 CPUs and about 13.6 GiB; one collection of about 236-byte documents with the `_id` index only.

Files:

- Alternated runs: [a million and 100,000 documents](alternated/1m-and-100k.txt), [10,000 changed at 100,000 and 10,000 documents](alternated/10000-changed-100k-and-10k.txt), [a million with every server operation logged](alternated/1m-10000-changed-every-operation-logged.txt) and [the server time inside each second diff](alternated/1m-10000-changed-server-time-in-second-diff.txt), [a million with a pause before the second diff](alternated/1m-10000-changed-paused.txt)
- Full run of 2.6.0: [generated report](report.md), [raw samples](raw.json), [provenance](provenance.json), [commands and output](commands.log)
- Full run of 2.5.0 in this session: [generated report](baseline-v2.5.0/report.md), [raw samples](baseline-v2.5.0/raw.json), [provenance](baseline-v2.5.0/provenance.json), [commands and output](baseline-v2.5.0/commands.log)
- [The two full runs side by side](alternated/sequential-tables.txt), and [containers and load on the host](host-load.txt) around them

Nothing in the output files was edited after the runs. The two scripts gained a timestamp around the second diff, a `PAUSE_BEFORE_SECOND_DIFF` setting and a `SLOWMS` setting between the first alternated run and the last; the measured steps did not change.

## The first diff on a branch

Alternated, 100 documents changed per branch, six rounds per size, milliseconds, median (min–max):

| | 100,000 documents | 1,000,000 documents |
|---|---:|---:|
| First `argon diff`, 2.5.0 | 332 (242–898) | 5,476 (2,429–8,589) |
| First `argon diff`, **2.6.0** | **84 (43–1,313)** | **173 (89–448)** |
| Second `argon diff`, 2.5.0 | 68 (33–1,095) | 93 (32–102) |
| Second `argon diff`, **2.6.0** | **48 (30–115)** | **110 (49–597)** |

At a million documents every one of the six first diffs took 2.4 seconds or more in 2.5.0 and under half a second in 2.6.0. In 2.6.0 the first diff on a branch costs about what a later one does.

With 10,000 documents changed per branch at a million documents (ten rounds over three runs), the first diff took 3.5 to 8.2 seconds in 2.5.0 and 1.2 to 3.1 seconds in 2.6.0.

The full runs agree: the median of five first diffs at a million documents with 100 changed was 5,778 ms (2,338–6,879) for 2.5.0 and 519 ms (403–804) for 2.6.0.

## What a checkout costs for it

The work did not disappear. In 2.5.0 the first diff read the oplog of the checkout; in 2.6.0 the checkout reads it while it copies. Whether that makes a checkout slower could not be settled on this machine:

| `argon checkout` of a new branch at 1,000,000 documents, ms | 2.5.0 | 2.6.0 |
|---|---:|---:|
| 100 changed, six rounds, median (min–max) | 28,320 (15,847–44,373) | 38,726 (19,567–47,768) |
| 10,000 changed, four rounds | 18,198 (11,066–23,794) | 22,598 (17,775–26,914) |
| 10,000 changed, two rounds, every operation logged | 26,450 (24,481–28,419) | 25,090 (23,280–26,901) |
| 10,000 changed, four rounds, paused | 29,506 (11,690–36,605) | 25,296 (17,256–38,834) |
| Sum of all sixteen rounds | 406 s | 457 s |

Over the sixteen rounds 2.6.0's checkouts took 12% longer in total, with 2.6.0 slower in some rounds and faster in others and a spread within each release several times larger than the difference. That is consistent with a modest cost and does not establish one. At 100,000 documents no difference shows (median 1,081 ms and 1,021 ms).

From `argon branches create` to the end of the first diff, which is what a run that diffs once waits for, the sixteen rounds at a million documents took 547 s in 2.5.0 and 519 s in 2.6.0. In the first run alone (100 changed) it was 211 s and 216 s.

**The two full runs must not be compared for checkout.** They show a checkout p50 of 60.8 s for 2.6.0 against 14.4 s for 2.5.0 at a million documents. The 2.6.0 run came first, under a host load of 16, and the alternated runs above do not reproduce a difference of that size. The same applies to the other million-document rows of those two runs.

## Later diffs run sooner after the copy

With 10,000 documents changed at a million documents, the second diff and the merge preview came out slower in 2.6.0 in every round:

| 1,000,000 documents, 10,000 changed, ms, median (min–max) | 2.5.0 | 2.6.0 |
|---|---:|---:|
| Second `argon diff`, four rounds | 808 (376–954) | 1,694 (1,333–2,071) |
| `argon merge preview`, four rounds | 583 (397–761) | 1,306 (1,186–1,488) |
| Second `argon diff`, four rounds, after a 10-second pause | 1,247 (1,122–1,324) | 1,292 (1,117–1,557) |
| `argon merge preview`, four rounds, after a 10-second pause | 856 (654–1,220) | 994 (549–1,277) |

The two releases send MongoDB the same operations for that diff. With every operation logged, a second diff was 342 to 387 operations examining the same 30,003 log entries in both; they took 420 and 502 ms of server time in the two 2.5.0 rounds and 853 and 910 ms in the two 2.6.0 rounds. No other long operation overlapped. What differs is when the diff runs: 2.5.0's first diff spends five to eight seconds on the oplog, so its second diff starts that much later after the million-document copy. With a 10-second pause before the second diff in both releases, the difference is gone.

So in 2.6.0 the commands that follow a large checkout run while MongoDB is still settling after the copy, and can each take longer than the same command a few seconds later. It did not show at 100,000 documents (second diff 720 ms and 700 ms with 10,000 changed, eight rounds) or with 100 documents changed. The pause run is four rounds on a busy machine; the explanation fits the measurements and was not tested further.

## Not measured

- Any of this on a quiet machine. No figure here should be read as what 2.6.0 does on an idle laptop; the v2.5.0 report's figures for the steps 2.6.0 did not change remain the reference.
- A first diff with `argon watch` or a managed capture running on the parent.
- Other writes to the deployment between a parent's last drain and the next one. They are still scanned; the engine's architecture notes say so.
- The experimental features in 2.6.0 (online import, `argon source`, write-back). They are off by default and no part of this report.
- The cases where a diff reads a whole collection, the garbage-collection case, concurrency, more than one collection, DumboDB or any other system.

## Reproduce

```sh
scripts/interleaved_release_docker.sh 2.5.0 2.6.0 "$PWD/results/alternated.txt" 1000000 6 100 1000000 4 10000 100000 6 100
PAUSE_BEFORE_SECOND_DIFF=10 scripts/interleaved_release_docker.sh 2.5.0 2.6.0 "$PWD/results/paused.txt" 1000000 4 10000
scripts/cli_scale_docker.sh 2.6.0 results/cli-scale-2.6.0
```
