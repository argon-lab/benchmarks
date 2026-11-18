# Argon 2.4.0 CLI workflow at 10000, 100000, 1000000 documents

Window: `2026-11-18T04:39:31Z` → `2026-11-18T04:52:53Z`. Complete: **True**.

Binary SHA256 `7da8a5b960a9985bf8f4c71fa235cdc0212dc80ed9c51e1e6fea8b9350ff3cff`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs and 13.6 GiB visible to the measuring process.

Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; with few samples the maximum is the observed maximum, not a tail estimate.

## 10000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 11.30 | 23.77 | 62.14 | 62.14 |
| `bulk_update_10000_ms` | 5 | 154.28 | 178.99 | 242.32 | 242.32 |
| `bulk_update_100_ms` | 5 | 2.91 | 3.43 | 3.90 | 3.90 |
| `capture_after_ack_10000_ms` | 5 | 312.14 | 313.83 | 325.68 | 325.68 |
| `capture_after_ack_100_ms` | 5 | 509.51 | 519.61 | 535.83 | 535.83 |
| `checkout_ms` | 10 | 69.88 | 75.40 | 128.62 | 128.62 |
| `diff_10000_changed_ms` | 15 | 123.14 | 163.14 | 290.44 | 290.44 |
| `diff_100_changed_ms` | 15 | 84.93 | 104.96 | 122.95 | 122.95 |
| `first_read_ms` | 10 | 1.46 | 1.66 | 3.73 | 3.73 |
| `import_ms` | 1 | 292.53 | 292.53 | 292.53 | 292.53 |
| `main_checkout_ms` | 1 | 104.90 | 104.90 | 104.90 | 104.90 |
| `merge_apply_10000_changed_ms` | 5 | 1903.85 | 2211.19 | 3289.96 | 3289.96 |
| `merge_apply_100_changed_ms` | 5 | 34.52 | 54.02 | 101.59 | 101.59 |
| `merge_preview_10000_changed_ms` | 5 | 154.70 | 181.10 | 195.03 | 195.03 |
| `merge_preview_100_changed_ms` | 5 | 85.27 | 88.39 | 131.93 | 131.93 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 2070.16 | 2406.22 | 3444.66 | 3444.66 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 122.91 | 160.98 | 233.51 | 233.51 |
| `new_branch_to_first_read_ms` | 10 | 86.81 | 108.97 | 178.21 | 178.21 |
| `point_read_by_id_us` | 1000 | 72.88 | 82.42 | 111.58 | 218.00 |
| `release_ms` | 10 | 112.72 | 127.06 | 131.47 | 131.47 |
| `sandbox_create_ms` | 5 | 104.72 | 111.58 | 157.48 | 157.48 |
| `sandbox_create_to_first_read_ms` | 5 | 106.87 | 113.25 | 160.40 | 160.40 |
| `sandbox_discard_ms` | 5 | 110.88 | 116.35 | 117.93 | 117.93 |
| `sandbox_first_read_ms` | 5 | 1.38 | 1.58 | 2.60 | 2.60 |
| `seed_native_insert_ms` | 1 | 82.53 | 82.53 | 82.53 | 82.53 |
| `watch_ready_ms` | 10 | 4.47 | 4.93 | 9.96 | 9.96 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 2343890 | 4096 | 4096 |
| metadata_after_import | 10007 | 5010089 | 32768 | 77824 |
| main_checkout | 10000 | 2343890 | 4096 | 4096 |
| branch_checkout | 10000 | 2343890 | 4096 | 4096 |
| metadata_at_end | 60555 | 77548565 | 19472384 | 19894272 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 67404
- `checkout`: 48720
- `branch_create`: 27244
- `diff`: 115328
- `merge_preview`: 125500
- `merge_apply`: 149816
- `release`: 27332
- `branch_delete`: 26628
- `sandbox_create`: 48792
- `sandbox_discard`: 26716

Merged updates verified in main: 50500; WAL entries at the end: 60512.

## 100000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 12.86 | 28.15 | 115.61 | 115.61 |
| `bulk_update_10000_ms` | 5 | 188.66 | 239.00 | 367.98 | 367.98 |
| `bulk_update_100_ms` | 5 | 4.26 | 5.09 | 10.48 | 10.48 |
| `capture_after_ack_10000_ms` | 5 | 357.38 | 413.27 | 483.47 | 483.47 |
| `capture_after_ack_100_ms` | 5 | 509.28 | 524.02 | 527.45 | 527.45 |
| `checkout_ms` | 10 | 619.40 | 707.78 | 1616.57 | 1616.57 |
| `diff_10000_changed_ms` | 15 | 501.23 | 677.57 | 1066.24 | 1066.24 |
| `diff_100_changed_ms` | 15 | 339.87 | 545.05 | 1574.02 | 1574.02 |
| `first_read_ms` | 10 | 2.09 | 2.81 | 8.13 | 8.13 |
| `import_ms` | 1 | 1591.82 | 1591.82 | 1591.82 | 1591.82 |
| `main_checkout_ms` | 1 | 744.32 | 744.32 | 744.32 | 744.32 |
| `merge_apply_10000_changed_ms` | 5 | 2610.80 | 2843.65 | 4037.08 | 4037.08 |
| `merge_apply_100_changed_ms` | 5 | 51.87 | 80.84 | 387.50 | 387.50 |
| `merge_preview_10000_changed_ms` | 5 | 559.89 | 681.27 | 760.59 | 760.59 |
| `merge_preview_100_changed_ms` | 5 | 357.47 | 430.90 | 536.03 | 536.03 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 3170.69 | 3552.61 | 4696.62 | 4696.62 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 414.70 | 521.48 | 923.53 | 923.53 |
| `new_branch_to_first_read_ms` | 10 | 695.16 | 756.32 | 1654.31 | 1654.31 |
| `point_read_by_id_us` | 1000 | 65.29 | 118.96 | 216.67 | 9757.75 |
| `release_ms` | 10 | 114.22 | 120.21 | 170.58 | 170.58 |
| `sandbox_create_ms` | 5 | 686.53 | 804.93 | 832.80 | 832.80 |
| `sandbox_create_to_first_read_ms` | 5 | 688.56 | 807.60 | 835.90 | 835.90 |
| `sandbox_discard_ms` | 5 | 111.52 | 113.14 | 115.10 | 115.10 |
| `sandbox_first_read_ms` | 5 | 1.81 | 2.17 | 2.90 | 2.90 |
| `seed_native_insert_ms` | 1 | 389.33 | 389.33 | 389.33 | 389.33 |
| `watch_ready_ms` | 10 | 5.32 | 6.51 | 13.74 | 13.74 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 23538890 | 4096 | 4096 |
| metadata_after_import | 100013 | 50142727 | 6344704 | 13709312 |
| main_checkout | 100000 | 23538890 | 1413120 | 1138688 |
| branch_checkout | 100000 | 23538890 | 4096 | 1134592 |
| metadata_at_end | 150597 | 125914997 | 35209216 | 42573824 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 300060
- `checkout`: 215516
- `branch_create`: 27156
- `diff`: 566764
- `merge_preview`: 543904
- `merge_apply`: 323208
- `release`: 27204
- `branch_delete`: 26712
- `sandbox_create`: 209020
- `sandbox_discard`: 26940

Merged updates verified in main: 50500; WAL entries at the end: 150512.

## 1000000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 14.24 | 30.69 | 84.38 | 84.38 |
| `bulk_update_10000_ms` | 5 | 496.76 | 1223.63 | 1434.87 | 1434.87 |
| `bulk_update_100_ms` | 5 | 15.54 | 18.74 | 42.26 | 42.26 |
| `capture_after_ack_10000_ms` | 5 | 356.96 | 812.62 | 1010.14 | 1010.14 |
| `capture_after_ack_100_ms` | 5 | 515.45 | 526.75 | 549.29 | 549.29 |
| `checkout_ms` | 10 | 7663.18 | 11391.98 | 15604.86 | 15604.86 |
| `diff_10000_changed_ms` | 15 | 5732.88 | 10142.66 | 14905.30 | 14905.30 |
| `diff_100_changed_ms` | 15 | 6468.45 | 12703.21 | 17304.75 | 17304.75 |
| `first_read_ms` | 10 | 3.91 | 6.27 | 16.93 | 16.93 |
| `import_ms` | 1 | 20631.15 | 20631.15 | 20631.15 | 20631.15 |
| `main_checkout_ms` | 1 | 8741.95 | 8741.95 | 8741.95 | 8741.95 |
| `merge_apply_10000_changed_ms` | 5 | 6420.39 | 7313.35 | 9916.93 | 9916.93 |
| `merge_apply_100_changed_ms` | 5 | 104.35 | 142.31 | 3463.16 | 3463.16 |
| `merge_preview_10000_changed_ms` | 5 | 7635.91 | 9357.80 | 11751.52 | 11751.52 |
| `merge_preview_100_changed_ms` | 5 | 7345.12 | 10221.84 | 15352.79 | 15352.79 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 14056.30 | 16599.30 | 21224.41 | 21224.41 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 7449.46 | 11391.60 | 15495.10 | 15495.10 |
| `new_branch_to_first_read_ms` | 10 | 7681.89 | 11494.57 | 15650.13 | 15650.13 |
| `point_read_by_id_us` | 1000 | 76.67 | 198.25 | 419.04 | 1597.08 |
| `release_ms` | 10 | 123.77 | 128.11 | 197.32 | 197.32 |
| `sandbox_create_ms` | 5 | 6751.97 | 9329.82 | 14462.78 | 14462.78 |
| `sandbox_create_to_first_read_ms` | 5 | 6754.81 | 9334.94 | 14473.83 | 14473.83 |
| `sandbox_discard_ms` | 5 | 110.71 | 118.48 | 132.68 | 132.68 |
| `sandbox_first_read_ms` | 5 | 2.56 | 4.32 | 9.51 | 9.51 |
| `seed_native_insert_ms` | 1 | 4510.52 | 4510.52 | 4510.52 | 4510.52 |
| `watch_ready_ms` | 10 | 7.05 | 10.50 | 38.58 | 38.58 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 236388890 | 32202752 | 26767360 |
| metadata_after_import | 1000070 | 502280173 | 72450048 | 178085888 |
| main_checkout | 1000000 | 236388890 | 44834816 | 30699520 |
| branch_checkout | 1000000 | 236388890 | 43270144 | 32653312 |
| metadata_at_end | 1050996 | 605037279 | 155795456 | 212660224 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 2856812
- `checkout`: 1951748
- `branch_create`: 26996
- `diff`: 5135828
- `merge_preview`: 5040748
- `merge_apply`: 2019092
- `release`: 27384
- `branch_delete`: 27032
- `sandbox_create`: 1794516
- `sandbox_discard`: 26704

Merged updates verified in main: 50500; WAL entries at the end: 1050512.
