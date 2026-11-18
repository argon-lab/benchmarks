# Argon 2.5.0 CLI workflow at 10000, 100000, 1000000 documents

Window: `2026-11-18T09:56:42Z` → `2026-11-18T10:12:20Z`. Complete: **True**.

Binary SHA256 `c1d5729895765f6131a2e83548ebe768af5b60374f1b24072251eb277482c880`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs and 13.6 GiB visible to the measuring process.

Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; with few samples the maximum is the observed maximum, not a tail estimate.

## 10000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 45.79 | 72.27 | 236.05 | 236.05 |
| `bulk_update_10000_ms` | 5 | 601.98 | 747.58 | 1124.84 | 1124.84 |
| `bulk_update_100_ms` | 5 | 14.84 | 20.50 | 36.15 | 36.15 |
| `capture_after_ack_10000_ms` | 5 | 749.93 | 829.76 | 1297.45 | 1297.45 |
| `capture_after_ack_100_ms` | 5 | 533.19 | 546.53 | 566.99 | 566.99 |
| `checkout_ms` | 10 | 207.37 | 288.13 | 545.11 | 545.11 |
| `diff_10000_changed_ms` | 15 | 552.17 | 884.86 | 1206.92 | 1206.92 |
| `diff_100_changed_ms` | 15 | 79.66 | 144.04 | 295.03 | 295.03 |
| `first_read_ms` | 10 | 6.80 | 9.08 | 16.90 | 16.90 |
| `import_ms` | 1 | 901.63 | 901.63 | 901.63 | 901.63 |
| `main_checkout_ms` | 1 | 382.57 | 382.57 | 382.57 | 382.57 |
| `merge_apply_10000_changed_ms` | 5 | 4764.49 | 5008.08 | 6091.47 | 6091.47 |
| `merge_apply_100_changed_ms` | 5 | 144.12 | 162.83 | 288.52 | 288.52 |
| `merge_preview_10000_changed_ms` | 5 | 548.28 | 951.03 | 1166.61 | 1166.61 |
| `merge_preview_100_changed_ms` | 5 | 87.07 | 110.81 | 131.32 | 131.32 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 5635.37 | 5959.11 | 6900.18 | 6900.18 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 236.06 | 279.76 | 399.33 | 399.33 |
| `new_branch_to_first_read_ms` | 10 | 289.85 | 421.13 | 745.48 | 745.48 |
| `point_read_by_id_us` | 1000 | 68.62 | 205.67 | 714.17 | 3937.58 |
| `release_ms` | 10 | 142.58 | 159.66 | 207.03 | 207.03 |
| `sandbox_create_ms` | 5 | 322.39 | 334.24 | 515.54 | 515.54 |
| `sandbox_create_to_first_read_ms` | 5 | 329.34 | 344.06 | 537.41 | 537.41 |
| `sandbox_discard_ms` | 5 | 133.33 | 144.68 | 187.41 | 187.41 |
| `sandbox_first_read_ms` | 5 | 6.34 | 8.69 | 21.34 | 21.34 |
| `seed_native_insert_ms` | 1 | 156.06 | 156.06 | 156.06 | 156.06 |
| `watch_ready_ms` | 10 | 13.04 | 18.42 | 52.23 | 52.23 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 2343890 | 4096 | 4096 |
| metadata_after_import | 10007 | 5010089 | 32768 | 77824 |
| main_checkout | 10000 | 2343890 | 4096 | 4096 |
| branch_checkout | 10000 | 2343890 | 4096 | 4096 |
| metadata_at_end | 60555 | 77558265 | 22089728 | 24899584 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 52324
- `checkout`: 46984
- `branch_create`: 25608
- `diff`: 125168
- `merge_preview`: 125208
- `merge_apply`: 161384
- `release`: 27208
- `branch_delete`: 23224
- `sandbox_create`: 49240
- `sandbox_discard`: 26828

Merged updates verified in main: 50500; WAL entries at the end: 60512.

## 100000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 33.22 | 85.25 | 265.69 | 265.69 |
| `bulk_update_10000_ms` | 5 | 684.52 | 834.14 | 1037.04 | 1037.04 |
| `bulk_update_100_ms` | 5 | 7.30 | 15.61 | 17.62 | 17.62 |
| `capture_after_ack_10000_ms` | 5 | 665.34 | 1168.23 | 2363.30 | 2363.30 |
| `capture_after_ack_100_ms` | 5 | 516.77 | 533.43 | 545.55 | 545.55 |
| `checkout_ms` | 10 | 1271.74 | 1869.45 | 3325.30 | 3325.30 |
| `diff_10000_changed_ms` | 15 | 586.65 | 987.87 | 2587.77 | 2587.77 |
| `diff_100_changed_ms` | 15 | 53.04 | 88.84 | 584.72 | 584.72 |
| `first_read_ms` | 10 | 3.94 | 7.68 | 19.08 | 19.08 |
| `import_ms` | 1 | 4275.11 | 4275.11 | 4275.11 | 4275.11 |
| `main_checkout_ms` | 1 | 2642.51 | 2642.51 | 2642.51 | 2642.51 |
| `merge_apply_10000_changed_ms` | 5 | 6471.87 | 7220.07 | 8914.69 | 8914.69 |
| `merge_apply_100_changed_ms` | 5 | 113.89 | 127.58 | 634.55 | 634.55 |
| `merge_preview_10000_changed_ms` | 5 | 815.71 | 893.79 | 929.68 | 929.68 |
| `merge_preview_100_changed_ms` | 5 | 55.97 | 77.58 | 103.08 | 103.08 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 7365.66 | 8055.11 | 9844.37 | 9844.37 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 183.56 | 224.15 | 725.07 | 725.07 |
| `new_branch_to_first_read_ms` | 10 | 1383.08 | 1918.08 | 3614.08 | 3614.08 |
| `point_read_by_id_us` | 1000 | 79.00 | 246.75 | 729.71 | 3972.71 |
| `release_ms` | 10 | 129.87 | 153.80 | 484.14 | 484.14 |
| `sandbox_create_ms` | 5 | 2076.88 | 2374.45 | 3201.14 | 3201.14 |
| `sandbox_create_to_first_read_ms` | 5 | 2089.72 | 2390.08 | 3220.80 | 3220.80 |
| `sandbox_discard_ms` | 5 | 143.00 | 145.57 | 170.84 | 170.84 |
| `sandbox_first_read_ms` | 5 | 12.18 | 14.26 | 17.77 | 17.77 |
| `seed_native_insert_ms` | 1 | 1151.90 | 1151.90 | 1151.90 | 1151.90 |
| `watch_ready_ms` | 10 | 9.80 | 17.51 | 28.36 | 28.36 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 23538890 | 946176 | 4096 |
| metadata_after_import | 100013 | 50142727 | 6344704 | 14045184 |
| main_checkout | 100000 | 23538890 | 2777088 | 1564672 |
| branch_checkout | 100000 | 23538890 | 3039232 | 1519616 |
| metadata_at_end | 150597 | 125895097 | 40083456 | 46465024 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 282900
- `checkout`: 208736
- `branch_create`: 24104
- `diff`: 114484
- `merge_preview`: 114932
- `merge_apply`: 316600
- `release`: 27328
- `branch_delete`: 25500
- `sandbox_create`: 220156
- `sandbox_discard`: 22960

Merged updates verified in main: 50500; WAL entries at the end: 150512.

## 1000000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 16.35 | 53.08 | 169.04 | 169.04 |
| `bulk_update_10000_ms` | 5 | 600.30 | 1022.58 | 1339.09 | 1339.09 |
| `bulk_update_100_ms` | 5 | 14.78 | 34.61 | 65.56 | 65.56 |
| `capture_after_ack_10000_ms` | 5 | 1113.82 | 1266.96 | 2234.61 | 2234.61 |
| `capture_after_ack_100_ms` | 5 | 511.50 | 546.90 | 552.47 | 552.47 |
| `checkout_ms` | 10 | 8555.95 | 14386.50 | 52512.20 | 52512.20 |
| `diff_10000_changed_ms` | 15 | 362.19 | 672.19 | 9217.13 | 9217.13 |
| `diff_100_changed_ms` | 15 | 33.95 | 80.29 | 6878.92 | 6878.92 |
| `first_read_ms` | 10 | 3.51 | 9.55 | 156.77 | 156.77 |
| `import_ms` | 1 | 74876.91 | 74876.91 | 74876.91 | 74876.91 |
| `main_checkout_ms` | 1 | 58344.37 | 58344.37 | 58344.37 | 58344.37 |
| `merge_apply_10000_changed_ms` | 5 | 6810.02 | 7580.54 | 12730.87 | 12730.87 |
| `merge_apply_100_changed_ms` | 5 | 219.96 | 286.91 | 4037.45 | 4037.45 |
| `merge_preview_10000_changed_ms` | 5 | 401.86 | 473.69 | 585.60 | 585.60 |
| `merge_preview_100_changed_ms` | 5 | 29.98 | 94.16 | 162.11 | 162.11 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 7283.71 | 8166.15 | 13308.34 | 13308.34 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 307.18 | 433.21 | 4067.43 | 4067.43 |
| `new_branch_to_first_read_ms` | 10 | 8607.95 | 14463.07 | 52587.72 | 52587.72 |
| `point_read_by_id_us` | 1000 | 106.46 | 461.17 | 1387.96 | 8158.29 |
| `release_ms` | 10 | 120.62 | 139.93 | 168.41 | 168.41 |
| `sandbox_create_ms` | 5 | 39607.52 | 40243.99 | 48850.58 | 48850.58 |
| `sandbox_create_to_first_read_ms` | 5 | 39655.69 | 40274.00 | 48887.82 | 48887.82 |
| `sandbox_discard_ms` | 5 | 132.50 | 146.26 | 169.44 | 169.44 |
| `sandbox_first_read_ms` | 5 | 13.04 | 28.39 | 44.44 | 44.44 |
| `seed_native_insert_ms` | 1 | 10299.16 | 10299.16 | 10299.16 | 10299.16 |
| `watch_ready_ms` | 10 | 6.93 | 11.74 | 57.78 | 57.78 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 236388890 | 34484224 | 29564928 |
| metadata_after_import | 1000070 | 502280173 | 72249344 | 177184768 |
| main_checkout | 1000000 | 236388890 | 43143168 | 32731136 |
| branch_checkout | 1000000 | 236388890 | 44834816 | 33783808 |
| metadata_at_end | 1050996 | 605037379 | 155332608 | 213864448 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 2405440
- `checkout`: 1789188
- `branch_create`: 27444
- `diff`: 119532
- `merge_preview`: 120456
- `merge_apply`: 2013052
- `release`: 27300
- `branch_delete`: 28916
- `sandbox_create`: 1996212
- `sandbox_discard`: 27108

Merged updates verified in main: 50500; WAL entries at the end: 1050512.
