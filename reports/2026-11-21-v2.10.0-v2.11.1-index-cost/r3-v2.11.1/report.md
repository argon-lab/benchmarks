# Argon 2.11.1: time from `sandbox create` to the first write

Window: `2026-11-21T08:51:35Z` → `2026-11-21T08:52:32Z`. Complete: **True**.

Binary SHA256 `ec9a7466cc0a932e9006342c26cb167030d294c832364b44f330ef7fa01ad7ad`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 507 | 504 | 510 |
| `checkout_ms` | 3 | 2062 | 2003 | 2276 |
| `create_to_first_write_ms` | 3 | 2210 | 2193 | 2351 |
| `first_write_ack_ms` | 3 | 7 | 6 | 10 |
| `fork_ms` | 3 | 17 | 16 | 22 |
| `import_ms` | 1 | 4859 | 4859 | 4859 |
| `ready_ms` | 3 | 2200 | 2187 | 2346 |
| `seed_ms` | 1 | 1068 | 1068 | 1068 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 6524928 | 2392064 |
| sandbox | 100001 | 102938932 | 8167424 | 1789952 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 3 | 508 | 506 | 509 |
| `checkout_ms` | 3 | 4325 | 4246 | 4502 |
| `create_to_first_write_ms` | 3 | 4263 | 4235 | 4281 |
| `first_write_ack_ms` | 3 | 9 | 8 | 13 |
| `fork_ms` | 3 | 21 | 19 | 22 |
| `import_ms` | 1 | 4849 | 4849 | 4849 |
| `ready_ms` | 3 | 4250 | 4226 | 4273 |
| `seed_ms` | 1 | 1292 | 1292 | 1292 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 10678272 | 11657216 |
| sandbox | 100001 | 102938932 | 9850880 | 6184960 |
