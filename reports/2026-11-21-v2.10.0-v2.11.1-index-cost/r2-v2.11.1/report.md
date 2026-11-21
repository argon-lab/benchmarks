# Argon 2.11.1: time from `sandbox create` to the first write

Window: `2026-11-21T08:49:35Z` → `2026-11-21T08:50:29Z`. Complete: **True**.

Binary SHA256 `ec9a7466cc0a932e9006342c26cb167030d294c832364b44f330ef7fa01ad7ad`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 507 | 506 | 508 |
| `checkout_ms` | 3 | 1857 | 1842 | 2076 |
| `create_to_first_write_ms` | 3 | 1798 | 1757 | 2042 |
| `first_write_ack_ms` | 3 | 6 | 5 | 7 |
| `fork_ms` | 3 | 17 | 14 | 21 |
| `import_ms` | 1 | 5042 | 5042 | 5042 |
| `ready_ms` | 3 | 1793 | 1751 | 2035 |
| `seed_ms` | 1 | 960 | 960 | 960 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 6643712 | 1097728 |
| sandbox | 100001 | 102938932 | 8351744 | 2285568 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 505 | 504 | 509 |
| `checkout_ms` | 3 | 4140 | 4069 | 4183 |
| `create_to_first_write_ms` | 3 | 4072 | 4062 | 4206 |
| `first_write_ack_ms` | 3 | 9 | 8 | 9 |
| `fork_ms` | 3 | 22 | 20 | 28 |
| `import_ms` | 1 | 5073 | 5073 | 5073 |
| `ready_ms` | 3 | 4064 | 4053 | 4197 |
| `seed_ms` | 1 | 1382 | 1382 | 1382 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 10665984 | 10960896 |
| sandbox | 100001 | 102938932 | 10969088 | 6557696 |
