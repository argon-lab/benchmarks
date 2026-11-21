# Argon 2.11.1: time from `sandbox create` to the first write

Window: `2026-11-21T08:47:34Z` → `2026-11-21T08:48:28Z`. Complete: **True**.

Binary SHA256 `ec9a7466cc0a932e9006342c26cb167030d294c832364b44f330ef7fa01ad7ad`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 507 | 507 | 509 |
| `checkout_ms` | 3 | 1717 | 1711 | 1791 |
| `create_to_first_write_ms` | 3 | 1749 | 1732 | 2048 |
| `first_write_ack_ms` | 3 | 6 | 5 | 9 |
| `fork_ms` | 3 | 18 | 14 | 18 |
| `import_ms` | 1 | 5483 | 5483 | 5483 |
| `ready_ms` | 3 | 1743 | 1727 | 2039 |
| `seed_ms` | 1 | 907 | 907 | 907 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 4022272 | 1425408 |
| sandbox | 100001 | 102938932 | 10330112 | 2494464 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 507 | 507 | 507 |
| `checkout_ms` | 3 | 4120 | 4054 | 4142 |
| `create_to_first_write_ms` | 3 | 4219 | 4182 | 4260 |
| `first_write_ack_ms` | 3 | 9 | 6 | 9 |
| `fork_ms` | 3 | 25 | 22 | 25 |
| `import_ms` | 1 | 4912 | 4912 | 4912 |
| `ready_ms` | 3 | 4210 | 4176 | 4251 |
| `seed_ms` | 1 | 1188 | 1188 | 1188 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 5644288 | 6713344 |
| sandbox | 100001 | 102938932 | 10940416 | 6475776 |
