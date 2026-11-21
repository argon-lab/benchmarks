# Argon 2.10.0: time from `sandbox create` to the first write

Window: `2026-11-21T08:48:41Z` → `2026-11-21T08:49:21Z`. Complete: **True**.

Binary SHA256 `3cec9b88b761ca915d1500b51b99a03f6453ecf3eed1e6dd0f239cb33e610747`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 506 | 505 | 510 |
| `checkout_ms` | 3 | 1798 | 1680 | 2380 |
| `create_to_first_write_ms` | 3 | 1988 | 1873 | 2147 |
| `first_write_ack_ms` | 3 | 5 | 5 | 7 |
| `fork_ms` | 3 | 15 | 14 | 16 |
| `import_ms` | 1 | 5049 | 5049 | 5049 |
| `ready_ms` | 3 | 1982 | 1868 | 2142 |
| `seed_ms` | 1 | 932 | 932 | 932 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 4624384 | 1425408 |
| sandbox | 100001 | 102938932 | 8765440 | 1720320 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 507 | 505 | 517 |
| `checkout_ms` | 3 | 1786 | 1621 | 2096 |
| `create_to_first_write_ms` | 3 | 1768 | 1705 | 1923 |
| `first_write_ack_ms` | 3 | 7 | 6 | 7 |
| `fork_ms` | 3 | 15 | 14 | 23 |
| `import_ms` | 1 | 4422 | 4422 | 4422 |
| `ready_ms` | 3 | 1761 | 1700 | 1916 |
| `seed_ms` | 1 | 1111 | 1111 | 1111 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 5623808 | 6930432 |
| sandbox | 100001 | 102938932 | 7573504 | 2105344 |
