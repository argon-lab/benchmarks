# Argon 2.6.0 CLI workflow at 10000, 100000, 1000000 documents

Window: `2026-11-18T09:31:22Z` → `2026-11-18T09:56:17Z`. Complete: **True**.

Binary SHA256 `edba0c2ecf6be346896ac0e3cc0b199515c0420a68c12a35cf2f19de12a7b113`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs and 13.6 GiB visible to the measuring process.

Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; with few samples the maximum is the observed maximum, not a tail estimate.

## 10000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 45.99 | 80.25 | 172.63 | 172.63 |
| `bulk_update_10000_ms` | 5 | 531.06 | 677.25 | 1209.68 | 1209.68 |
| `bulk_update_100_ms` | 5 | 9.04 | 16.89 | 18.40 | 18.40 |
| `capture_after_ack_10000_ms` | 5 | 679.41 | 1052.41 | 1884.19 | 1884.19 |
| `capture_after_ack_100_ms` | 5 | 528.48 | 539.00 | 541.73 | 541.73 |
| `checkout_ms` | 10 | 246.57 | 323.85 | 722.60 | 722.60 |
| `diff_10000_changed_ms` | 15 | 726.74 | 1066.73 | 1789.96 | 1789.96 |
| `diff_100_changed_ms` | 15 | 55.45 | 110.86 | 214.46 | 214.46 |
| `first_read_ms` | 10 | 5.05 | 8.24 | 81.48 | 81.48 |
| `import_ms` | 1 | 798.45 | 798.45 | 798.45 | 798.45 |
| `main_checkout_ms` | 1 | 396.43 | 396.43 | 396.43 | 396.43 |
| `merge_apply_10000_changed_ms` | 5 | 6108.23 | 6468.19 | 7366.96 | 7366.96 |
| `merge_apply_100_changed_ms` | 5 | 137.31 | 185.16 | 383.83 | 383.83 |
| `merge_preview_10000_changed_ms` | 5 | 690.27 | 1106.56 | 1436.79 | 1436.79 |
| `merge_preview_100_changed_ms` | 5 | 72.59 | 97.47 | 117.62 | 117.62 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 6798.50 | 7611.52 | 8406.31 | 8406.31 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 213.03 | 293.87 | 501.45 | 501.45 |
| `new_branch_to_first_read_ms` | 10 | 298.42 | 412.16 | 949.32 | 949.32 |
| `point_read_by_id_us` | 1000 | 77.04 | 377.92 | 1701.88 | 9483.46 |
| `release_ms` | 10 | 154.99 | 162.20 | 274.69 | 274.69 |
| `sandbox_create_ms` | 5 | 605.93 | 631.39 | 835.49 | 835.49 |
| `sandbox_create_to_first_read_ms` | 5 | 615.21 | 660.34 | 847.26 | 847.26 |
| `sandbox_discard_ms` | 5 | 156.55 | 165.64 | 243.81 | 243.81 |
| `sandbox_first_read_ms` | 5 | 7.91 | 9.92 | 28.04 | 28.04 |
| `seed_native_insert_ms` | 1 | 110.76 | 110.76 | 110.76 | 110.76 |
| `watch_ready_ms` | 10 | 12.80 | 21.70 | 45.19 | 45.19 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 2343890 | 4096 | 4096 |
| metadata_after_import | 10007 | 5010089 | 40960 | 98304 |
| main_checkout | 10000 | 2343890 | 4096 | 4096 |
| branch_checkout | 10000 | 2343890 | 4096 | 4096 |
| metadata_at_end | 60555 | 77558849 | 21344256 | 25190400 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 51268
- `checkout`: 46152
- `branch_create`: 22196
- `diff`: 124220
- `merge_preview`: 123484
- `merge_apply`: 143552
- `release`: 23972
- `branch_delete`: 25012
- `sandbox_create`: 46996
- `sandbox_discard`: 21300

Merged updates verified in main: 50500; WAL entries at the end: 60512.

## 100000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 53.32 | 99.33 | 291.30 | 291.30 |
| `bulk_update_10000_ms` | 5 | 884.73 | 1062.67 | 1983.81 | 1983.81 |
| `bulk_update_100_ms` | 5 | 20.08 | 31.01 | 37.65 | 37.65 |
| `capture_after_ack_10000_ms` | 5 | 1171.99 | 1283.61 | 2511.97 | 2511.97 |
| `capture_after_ack_100_ms` | 5 | 534.25 | 550.70 | 620.19 | 620.19 |
| `checkout_ms` | 10 | 2613.44 | 3305.49 | 5979.75 | 5979.75 |
| `diff_10000_changed_ms` | 15 | 975.26 | 1437.04 | 1915.97 | 1915.97 |
| `diff_100_changed_ms` | 15 | 109.83 | 186.19 | 544.55 | 544.55 |
| `first_read_ms` | 10 | 8.07 | 18.11 | 50.14 | 50.14 |
| `import_ms` | 1 | 9310.48 | 9310.48 | 9310.48 | 9310.48 |
| `main_checkout_ms` | 1 | 3843.01 | 3843.01 | 3843.01 | 3843.01 |
| `merge_apply_10000_changed_ms` | 5 | 6812.13 | 8798.40 | 11668.71 | 11668.71 |
| `merge_apply_100_changed_ms` | 5 | 183.78 | 324.63 | 1293.55 | 1293.55 |
| `merge_preview_10000_changed_ms` | 5 | 994.93 | 1428.19 | 2275.93 | 2275.93 |
| `merge_preview_100_changed_ms` | 5 | 122.23 | 191.74 | 487.90 | 487.90 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 7807.06 | 11074.33 | 12949.30 | 12949.30 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 350.63 | 450.88 | 1781.45 | 1781.45 |
| `new_branch_to_first_read_ms` | 10 | 2764.96 | 3530.38 | 6132.73 | 6132.73 |
| `point_read_by_id_us` | 1000 | 103.00 | 276.71 | 1413.46 | 23589.67 |
| `release_ms` | 10 | 144.92 | 173.37 | 339.34 | 339.34 |
| `sandbox_create_ms` | 5 | 2147.58 | 2189.41 | 3069.14 | 3069.14 |
| `sandbox_create_to_first_read_ms` | 5 | 2156.28 | 2203.58 | 3107.80 | 3107.80 |
| `sandbox_discard_ms` | 5 | 143.29 | 148.86 | 178.73 | 178.73 |
| `sandbox_first_read_ms` | 5 | 6.10 | 12.90 | 36.72 | 36.72 |
| `seed_native_insert_ms` | 1 | 2244.17 | 2244.17 | 2244.17 | 2244.17 |
| `watch_ready_ms` | 10 | 16.61 | 31.71 | 85.72 | 85.72 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 23538890 | 2994176 | 2494464 |
| metadata_after_import | 100013 | 50142727 | 6737920 | 17424384 |
| main_checkout | 100000 | 23538890 | 3911680 | 2195456 |
| branch_checkout | 100000 | 23538890 | 1179648 | 1003520 |
| metadata_at_end | 150597 | 125895381 | 38313984 | 46583808 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 284636
- `checkout`: 224604
- `branch_create`: 23448
- `diff`: 115180
- `merge_preview`: 121928
- `merge_apply`: 333336
- `release`: 24856
- `branch_delete`: 22904
- `sandbox_create`: 207232
- `sandbox_discard`: 20488

Merged updates verified in main: 50500; WAL entries at the end: 150512.

## 1000000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 69.82 | 117.25 | 220.64 | 220.64 |
| `bulk_update_10000_ms` | 5 | 2579.77 | 3188.86 | 7759.95 | 7759.95 |
| `bulk_update_100_ms` | 5 | 60.90 | 122.13 | 282.92 | 282.92 |
| `capture_after_ack_10000_ms` | 5 | 1194.36 | 2897.36 | 5700.61 | 5700.61 |
| `capture_after_ack_100_ms` | 5 | 543.55 | 565.51 | 728.45 | 728.45 |
| `checkout_ms` | 10 | 41863.52 | 60751.52 | 85557.56 | 85557.56 |
| `diff_10000_changed_ms` | 15 | 1614.79 | 3311.49 | 9573.69 | 9573.69 |
| `diff_100_changed_ms` | 15 | 124.45 | 256.36 | 803.63 | 803.63 |
| `first_read_ms` | 10 | 12.85 | 33.60 | 282.67 | 282.67 |
| `import_ms` | 1 | 65018.30 | 65018.30 | 65018.30 | 65018.30 |
| `main_checkout_ms` | 1 | 50519.86 | 50519.86 | 50519.86 | 50519.86 |
| `merge_apply_10000_changed_ms` | 5 | 17811.37 | 25484.50 | 34241.28 | 34241.28 |
| `merge_apply_100_changed_ms` | 5 | 514.67 | 639.98 | 20599.93 | 20599.93 |
| `merge_preview_10000_changed_ms` | 5 | 1551.79 | 2954.29 | 3202.69 | 3202.69 |
| `merge_preview_100_changed_ms` | 5 | 125.32 | 169.48 | 271.56 | 271.56 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 20942.27 | 27036.29 | 36505.72 | 36505.72 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 781.86 | 816.61 | 20769.41 | 20769.41 |
| `new_branch_to_first_read_ms` | 10 | 42103.32 | 60844.92 | 85771.66 | 85771.66 |
| `point_read_by_id_us` | 1000 | 126.67 | 614.96 | 3854.29 | 11643.88 |
| `release_ms` | 10 | 154.61 | 199.99 | 319.48 | 319.48 |
| `sandbox_create_ms` | 5 | 20147.56 | 36492.91 | 49371.77 | 49371.77 |
| `sandbox_create_to_first_read_ms` | 5 | 20155.69 | 36523.17 | 49397.78 | 49397.78 |
| `sandbox_discard_ms` | 5 | 145.34 | 160.53 | 197.15 | 197.15 |
| `sandbox_first_read_ms` | 5 | 7.15 | 20.02 | 35.79 | 35.79 |
| `seed_native_insert_ms` | 1 | 11634.77 | 11634.77 | 11634.77 | 11634.77 |
| `watch_ready_ms` | 10 | 28.20 | 45.24 | 107.13 | 107.13 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 236388890 | 33042432 | 28528640 |
| metadata_after_import | 1000070 | 502280173 | 70660096 | 173928448 |
| main_checkout | 1000000 | 236388890 | 44437504 | 33136640 |
| branch_checkout | 1000000 | 236388890 | 44388352 | 38596608 |
| metadata_at_end | 1050996 | 605037361 | 143130624 | 208609280 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 2308040
- `checkout`: 2050908
- `branch_create`: 25420
- `diff`: 115380
- `merge_preview`: 122724
- `merge_apply`: 2067388
- `release`: 25420
- `branch_delete`: 24088
- `sandbox_create`: 1724068
- `sandbox_discard`: 24672

Merged updates verified in main: 50500; WAL entries at the end: 1050512.
