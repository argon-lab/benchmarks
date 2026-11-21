# Argon 2.9.0: time from `sandbox create` to the first write

Window: `2026-11-21T03:24:35Z` → `2026-11-21T03:38:23Z`. Complete: **True**.

Binary SHA256 `c26620d7b4ca311d8affc52ee4e91f453feb54fe5485ed5b6e20176c265f0ee8`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs visible.

Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.

## 10,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 8 | 506 | 503 | 507 |
| `checkout_ms` | 8 | 183 | 166 | 216 |
| `create_to_first_write_ms` | 8 | 222 | 203 | 271 |
| `first_write_ack_ms` | 8 | 4 | 3 | 9 |
| `fork_ms` | 8 | 13 | 9 | 18 |
| `import_ms` | 1 | 605 | 605 | 605 |
| `ready_ms` | 8 | 217 | 198 | 264 |
| `seed_ms` | 1 | 113 | 113 | 113 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 10283890 | 4096 | 4096 |
| sandbox | 10001 | 10283932 | 12288 | 290816 |

## 100,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 8 | 510 | 504 | 528 |
| `checkout_ms` | 8 | 2396 | 2024 | 3699 |
| `concurrent_first_write_ack_ms@1` | 8 | 7 | 5 | 13 |
| `concurrent_first_write_ack_ms@16` | 128 | 4 | 2 | 23 |
| `concurrent_first_write_ack_ms@4` | 32 | 3 | 1 | 9 |
| `concurrent_group_wall_ms@1` | 8 | 2240 | 1642 | 3192 |
| `concurrent_group_wall_ms@16` | 8 | 11068 | 9139 | 12073 |
| `concurrent_group_wall_ms@4` | 8 | 2591 | 1825 | 3571 |
| `concurrent_ready_ms@1` | 8 | 2240 | 1642 | 3192 |
| `concurrent_ready_ms@16` | 128 | 10906 | 9011 | 12072 |
| `concurrent_ready_ms@4` | 32 | 2578 | 1805 | 3569 |
| `create_to_first_write_ms` | 8 | 2381 | 1968 | 2921 |
| `first_write_ack_ms` | 8 | 10 | 6 | 27 |
| `fork_ms` | 8 | 23 | 16 | 34 |
| `import_ms` | 1 | 3858 | 3858 | 3858 |
| `ready_ms` | 8 | 2371 | 1960 | 2904 |
| `seed_ms` | 1 | 666 | 666 | 666 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 7610368 | 1097728 |
| sandbox | 100001 | 102938932 | 9027584 | 2015232 |

## 1,000,000 documents in 1 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 8 | 506 | 503 | 509 |
| `checkout_ms` | 8 | 17341 | 12587 | 20588 |
| `create_to_first_write_ms` | 8 | 16047 | 13654 | 20448 |
| `first_write_ack_ms` | 8 | 6 | 4 | 12 |
| `fork_ms` | 8 | 12 | 8 | 17 |
| `import_ms` | 1 | 37690 | 37690 | 37690 |
| `ready_ms` | 8 | 16043 | 13648 | 20439 |
| `seed_ms` | 1 | 5325 | 5325 | 5325 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 1030388890 | 107708416 | 30597120 |
| sandbox | 1000001 | 1030388932 | 109809664 | 33566720 |

## 100,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 8 | 505 | 502 | 522 |
| `checkout_ms` | 8 | 1376 | 1264 | 1589 |
| `create_to_first_write_ms` | 8 | 1391 | 1358 | 1501 |
| `first_write_ack_ms` | 8 | 5 | 3 | 6 |
| `fork_ms` | 8 | 12 | 9 | 15 |
| `import_ms` | 1 | 4451 | 4451 | 4451 |
| `ready_ms` | 8 | 1386 | 1355 | 1496 |
| `seed_ms` | 1 | 1092 | 1092 | 1092 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 102938890 | 8781824 | 10768384 |
| sandbox | 100001 | 102938932 | 9224192 | 2478080 |

## 1,000,000 documents in 10 collection(s)

| Measure | n | median | min | max |
|---|---:|---:|---:|---:|
| `ack_to_captured_ms` | 8 | 506 | 503 | 514 |
| `checkout_ms` | 8 | 13462 | 11031 | 14648 |
| `create_to_first_write_ms` | 8 | 13072 | 10807 | 14709 |
| `first_write_ack_ms` | 8 | 7 | 6 | 14 |
| `fork_ms` | 8 | 13 | 8 | 20 |
| `import_ms` | 1 | 37876 | 37876 | 37876 |
| `ready_ms` | 8 | 13059 | 10801 | 14703 |
| `seed_ms` | 1 | 10014 | 10014 | 10014 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 1030388890 | 107843584 | 123215872 |
| sandbox | 1000001 | 1030388932 | 108683264 | 31244288 |
