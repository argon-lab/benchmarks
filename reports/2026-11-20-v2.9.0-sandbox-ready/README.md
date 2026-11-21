# Argon 2.9.0: time from `sandbox create` to the first write

What an agent waits for before it can write to a new sandbox, measured with the published CLI.

- **Engine:** `npm install -g argonctl@2.9.0`. The executable the launcher starts, `bin/argon-bin`, has SHA256 `c26620d7b4ca311d8affc52ee4e91f453feb54fe5485ed5b6e20176c265f0ee8`, which matches the package's `checksums.json`.
- **MongoDB:** `mongo:7.0.45`, single-member replica set, WiredTiger cache 2 GiB.
- **Layout:** two containers sharing one network namespace, no published ports.
- **Window:** `2026-11-21T03:24:35Z` → `03:38:23Z`.
- **Scripts:** `scripts/sandbox_ready.py` and `scripts/sandbox_ready_docker.sh`, which reuse helpers from `scripts/cli_scale.py`. Their SHA256 hashes are in `provenance.json`. They were uncommitted when the run started, hence `dirty: true`; the committed files have the same hashes.

## What is timed

All times are monotonic wall clock inside the runner container.

**`ready_ms`** starts when `argon sandbox create -p <project> --name <n> --watch --output json` launches and stops when its JSON reply is complete. At that point the sandbox is forked, checked out and its capture is running.

**`first_write_ack_ms`** is a fresh driver connection to the returned connection string plus one `insert_one` with majority write concern. **`create_to_first_write_ms`** is the sum of the two.

**`ack_to_captured_ms`** runs from the acknowledgement until the write is visible in Argon's WAL, polling every 2 ms.

**`fork_ms`** and **`checkout_ms`** time `argon branches create` and `argon checkout` on a second fresh branch in the same round. They show where the ready time goes. Capture start-up is not timed separately.

**Concurrency** (100,000 documents, one collection): 1, 4 or 16 `sandbox create --watch` processes start at once from `main`. Recorded per process is its ready time, then each sandbox's first write. Recorded per group is the wall time until all are ready.

**Documents** have a string `_id`, five small fields and a 900-byte payload, about 1 KB of BSON each.
- *One collection:* only the `_id` index.
- *Ten collections:* each has a compound secondary index and a unique secondary index in the source.

Argon does not copy indexes, validators or collection options, so sandboxes have only `_id` indexes. This is a documented limitation, and the allocated index sizes in `report.md` show it.

Eight rounds per cell. Medians with min–max. No warm-up was discarded.

## Limits

- **Shared host.** During the run another session's containers ran on the same Docker VM: three `lf-mac-*` containers at a time, plus two idle `argon-follow-mongo` containers. The host load average was between 5.3 and 16.9 on 12 CPUs. `host-load.log` has a sample every 30 seconds. Absolute figures are therefore higher than on an idle machine. They are figures for this environment, not an SLA.
- **Small samples.** Eight samples give a median and a range, not tail latency.
- **One environment.** One MongoDB node on local Docker storage. A remote or replicated deployment adds network and replication time to every copy.

## Files

| File | Contents |
|---|---|
| `raw.json` | every sample and the environment |
| `report.md` | generated tables |
| `commands.log` | every CLI command with its output |
| `host-load.log` | host load and running containers, every 30 s |
| `provenance.json` | npm package, binary, images, host |
| `mongod.log.gz` | the server log for the window |

## Reproduce

```sh
scripts/sandbox_ready_docker.sh 2.9.0 <new results directory>
```
