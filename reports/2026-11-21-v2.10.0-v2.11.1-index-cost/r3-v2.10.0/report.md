# Argon 2.10.0: time from `sandbox create` to the first write

Window: `2026-11-21T08:50:43Z` → `2026-11-21T08:51:21Z`. Complete: **True**.

Binary SHA256 `3cec9b88b761ca915d1500b51b99a03f6453ecf3eed1e6dd0f239cb33e610747`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 506 | 505 | 511 |
| `checkout_ms` | 3 | 1911 | 1784 | 2214 |
| `create_to_first_write_ms` | 3 | 1987 | 1892 | 2017 |
| `first_write_ack_ms` | 3 | 7 | 6 | 8 |
| `fork_ms` | 3 | 16 | 15 | 22 |
| `import_ms` | 1 | 4749 | 4749 | 4749 |
| `ready_ms` | 3 | 1980 | 1886 | 2009 |
| `seed_ms` | 1 | 896 | 896 | 896 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 8032256 | 2064384 |
| sandbox | 100001 | 102938932 | 9277440 | 3219456 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 515 | 506 | 515 |
| `checkout_ms` | 3 | 1653 | 1524 | 1707 |
| `create_to_first_write_ms` | 3 | 1653 | 1620 | 1692 |
| `first_write_ack_ms` | 3 | 6 | 6 | 7 |
| `fork_ms` | 3 | 17 | 17 | 18 |
| `import_ms` | 1 | 4422 | 4422 | 4422 |
| `ready_ms` | 3 | 1646 | 1614 | 1686 |
| `seed_ms` | 1 | 1227 | 1227 | 1227 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 8757248 | 9867264 |
| sandbox | 100001 | 102938932 | 10985472 | 2912256 |
