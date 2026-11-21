# Argon 2.10.0: time from `sandbox create` to the first write

Window: `2026-11-21T08:46:38Z` → `2026-11-21T08:47:20Z`. Complete: **True**.

Binary SHA256 `3cec9b88b761ca915d1500b51b99a03f6453ecf3eed1e6dd0f239cb33e610747`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 507 | 504 | 507 |
| `checkout_ms` | 3 | 2145 | 1929 | 2290 |
| `create_to_first_write_ms` | 3 | 1762 | 1674 | 2327 |
| `first_write_ack_ms` | 3 | 6 | 6 | 7 |
| `fork_ms` | 3 | 18 | 16 | 20 |
| `import_ms` | 1 | 4908 | 4908 | 4908 |
| `ready_ms` | 3 | 1756 | 1668 | 2319 |
| `seed_ms` | 1 | 831 | 831 | 831 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 7344128 | 1097728 |
| sandbox | 100001 | 102938932 | 9834496 | 2531328 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 506 | 505 | 507 |
| `checkout_ms` | 3 | 1765 | 1505 | 1917 |
| `create_to_first_write_ms` | 3 | 1773 | 1699 | 2561 |
| `first_write_ack_ms` | 3 | 8 | 5 | 9 |
| `fork_ms` | 3 | 21 | 16 | 24 |
| `import_ms` | 1 | 5485 | 5485 | 5485 |
| `ready_ms` | 3 | 1765 | 1694 | 2553 |
| `seed_ms` | 1 | 1503 | 1503 | 1503 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 9932800 | 9592832 |
| sandbox | 100001 | 102938932 | 10960896 | 3022848 |
