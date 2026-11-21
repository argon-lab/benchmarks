# What building indexes adds to a sandbox: 2.10.0 against 2.11.1

From 2.11.0 a checkout builds each collection's recorded secondary indexes after copying its documents. This run measures what that adds to the time an agent waits for a sandbox.

**Releases**, both from npm:
- `argonctl@2.10.0`: binary SHA256 `3cec9b88b761ca915d1500b51b99a03f6453ecf3eed1e6dd0f239cb33e610747`
- `argonctl@2.11.1`: binary SHA256 `ec9a7466cc0a932e9006342c26cb167030d294c832364b44f330ef7fa01ad7ad`

**Script:** `scripts/sandbox_ready_docker.sh <version> <dir> --fixtures 100000:one,100000:ten --rounds 3 --concurrency ''`.

**Schedule:** three rounds for each release, alternated 2.10.0, 2.11.1, 2.10.0, … so that both see the same background load. `schedule.log` has the start times and load averages.

**Fixtures:**
- **One collection:** 100,000 documents of about 1 KB with only the `_id` index. This is the control.
- **Ten collections:** 10,000 documents each, with a compound and a unique secondary index in the source, 20 secondary indexes in all.

Each sandbox is a full copy; 2.10.0 copies documents only.

Milliseconds, median (min–max) of nine sandboxes per cell:

| Fixture | 2.10.0 ready | 2.11.1 ready | 2.10.0 checkout | 2.11.1 checkout |
|---|---:|---:|---:|---:|
| 1 collection, no secondary indexes | 1,980 (1,668–2,319) | 2,035 (1,727–2,346) | 1,929 (1,680–2,380) | 1,857 (1,711–2,276) |
| 10 collections, 20 secondary indexes | 1,700 (1,614–2,553) | 4,210 (4,053–4,273) | 1,707 (1,505–2,096) | 4,142 (4,054–4,502) |

- **Without secondary indexes nothing changed:** the medians differ by about 3% with overlapping ranges.
- **With 20 secondary indexes,** a 100,000-document sandbox takes about 2.5 s longer to be ready. The ranges do not overlap.
- **The first write** after the sandbox is ready still takes single-digit milliseconds.

**Limits:**
- The host is a shared developer machine. Another session's containers were running, and the load average was 11 to 13 on 12 CPUs throughout (`host-load.log` in each run directory). Absolute figures are inflated, but the comparison holds because the releases alternated.
- Nine samples give a median and a range, not tail latency.
- Index build time depends on the index types and on the data. These figures are for this environment, not an SLA.
