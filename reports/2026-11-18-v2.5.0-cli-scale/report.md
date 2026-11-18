# Argon 2.5.0 CLI workflow at 10000, 100000, 1000000 documents

Window: `2026-11-18T04:33:22Z` → `2026-11-18T04:39:13Z`. Complete: **True**.

Binary SHA256 `c1d5729895765f6131a2e83548ebe768af5b60374f1b24072251eb277482c880`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs and 13.6 GiB visible to the measuring process.

Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; with few samples the maximum is the observed maximum, not a tail estimate.

## 10000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 13.76 | 17.76 | 67.59 | 67.59 |
| `bulk_update_10000_ms` | 5 | 154.34 | 307.21 | 852.35 | 852.35 |
| `bulk_update_100_ms` | 5 | 3.20 | 4.41 | 4.78 | 4.78 |
| `capture_after_ack_10000_ms` | 5 | 297.01 | 350.29 | 389.42 | 389.42 |
| `capture_after_ack_100_ms` | 5 | 513.39 | 528.57 | 542.23 | 542.23 |
| `checkout_ms` | 10 | 75.35 | 103.11 | 147.18 | 147.18 |
| `diff_10000_changed_ms` | 15 | 246.22 | 392.57 | 777.87 | 777.87 |
| `diff_100_changed_ms` | 15 | 19.67 | 35.15 | 150.16 | 150.16 |
| `first_read_ms` | 10 | 1.53 | 1.87 | 10.05 | 10.05 |
| `import_ms` | 1 | 263.10 | 263.10 | 263.10 | 263.10 |
| `main_checkout_ms` | 1 | 85.12 | 85.12 | 85.12 | 85.12 |
| `merge_apply_10000_changed_ms` | 5 | 2314.51 | 2624.31 | 3234.31 | 3234.31 |
| `merge_apply_100_changed_ms` | 5 | 39.25 | 45.63 | 79.12 | 79.12 |
| `merge_preview_10000_changed_ms` | 5 | 325.76 | 386.15 | 491.41 | 491.41 |
| `merge_preview_100_changed_ms` | 5 | 24.84 | 26.64 | 52.80 | 52.80 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 2640.27 | 2962.55 | 3649.22 | 3649.22 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 65.89 | 76.72 | 103.96 | 103.96 |
| `new_branch_to_first_read_ms` | 10 | 90.97 | 135.06 | 225.36 | 225.36 |
| `point_read_by_id_us` | 1000 | 70.33 | 84.88 | 157.42 | 498.33 |
| `release_ms` | 10 | 115.32 | 122.29 | 144.85 | 144.85 |
| `sandbox_create_ms` | 5 | 147.38 | 182.72 | 203.35 | 203.35 |
| `sandbox_create_to_first_read_ms` | 5 | 149.62 | 186.32 | 205.95 | 205.95 |
| `sandbox_discard_ms` | 5 | 118.61 | 125.37 | 139.56 | 139.56 |
| `sandbox_first_read_ms` | 5 | 1.79 | 2.27 | 3.57 | 3.57 |
| `seed_native_insert_ms` | 1 | 108.61 | 108.61 | 108.61 | 108.61 |
| `watch_ready_ms` | 10 | 4.68 | 5.90 | 13.31 | 13.31 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 2343890 | 4096 | 4096 |
| metadata_after_import | 10007 | 5010089 | 32768 | 77824 |
| main_checkout | 10000 | 2343890 | 4096 | 4096 |
| branch_checkout | 10000 | 2343890 | 4096 | 4096 |
| metadata_at_end | 60555 | 77558265 | 21078016 | 20094976 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 64140
- `checkout`: 50732
- `branch_create`: 26792
- `diff`: 125856
- `merge_preview`: 122688
- `merge_apply`: 163236
- `release`: 27340
- `branch_delete`: 26836
- `sandbox_create`: 50692
- `sandbox_discard`: 26668

Merged updates verified in main: 50500; WAL entries at the end: 60512.

## 100000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 13.04 | 31.40 | 84.26 | 84.26 |
| `bulk_update_10000_ms` | 5 | 166.16 | 229.29 | 375.17 | 375.17 |
| `bulk_update_100_ms` | 5 | 3.97 | 5.85 | 26.18 | 26.18 |
| `capture_after_ack_10000_ms` | 5 | 321.39 | 373.64 | 443.56 | 443.56 |
| `capture_after_ack_100_ms` | 5 | 531.58 | 537.57 | 544.55 | 544.55 |
| `checkout_ms` | 10 | 616.72 | 737.93 | 1410.57 | 1410.57 |
| `diff_10000_changed_ms` | 15 | 312.93 | 449.64 | 797.06 | 797.06 |
| `diff_100_changed_ms` | 15 | 25.89 | 44.44 | 462.98 | 462.98 |
| `first_read_ms` | 10 | 1.55 | 2.50 | 8.57 | 8.57 |
| `import_ms` | 1 | 4064.84 | 4064.84 | 4064.84 | 4064.84 |
| `main_checkout_ms` | 1 | 1471.77 | 1471.77 | 1471.77 | 1471.77 |
| `merge_apply_10000_changed_ms` | 5 | 2282.07 | 2594.69 | 2857.44 | 2857.44 |
| `merge_apply_100_changed_ms` | 5 | 44.64 | 56.13 | 573.06 | 573.06 |
| `merge_preview_10000_changed_ms` | 5 | 367.30 | 414.91 | 446.50 | 446.50 |
| `merge_preview_100_changed_ms` | 5 | 23.93 | 39.09 | 82.01 | 82.01 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 2656.70 | 3037.72 | 3303.94 | 3303.94 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 69.55 | 95.22 | 613.96 | 613.96 |
| `new_branch_to_first_read_ms` | 10 | 631.87 | 797.71 | 1447.54 | 1447.54 |
| `point_read_by_id_us` | 1000 | 53.25 | 73.33 | 121.29 | 53575.38 |
| `release_ms` | 10 | 116.14 | 121.80 | 158.90 | 158.90 |
| `sandbox_create_ms` | 5 | 743.17 | 982.83 | 1131.11 | 1131.11 |
| `sandbox_create_to_first_read_ms` | 5 | 745.94 | 989.50 | 1135.10 | 1135.10 |
| `sandbox_discard_ms` | 5 | 112.84 | 120.60 | 216.94 | 216.94 |
| `sandbox_first_read_ms` | 5 | 2.53 | 3.37 | 7.01 | 7.01 |
| `seed_native_insert_ms` | 1 | 473.11 | 473.11 | 473.11 | 473.11 |
| `watch_ready_ms` | 10 | 4.74 | 6.83 | 15.39 | 15.39 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 23538890 | 4096 | 4096 |
| metadata_after_import | 100013 | 50142727 | 7237632 | 17186816 |
| main_checkout | 100000 | 23538890 | 1835008 | 1273856 |
| branch_checkout | 100000 | 23538890 | 4096 | 1232896 |
| metadata_at_end | 150597 | 125905297 | 33796096 | 42708992 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 310000
- `checkout`: 211448
- `branch_create`: 27436
- `diff`: 117928
- `merge_preview`: 116448
- `merge_apply`: 329980
- `release`: 27484
- `branch_delete`: 26664
- `sandbox_create`: 209040
- `sandbox_discard`: 25796

Merged updates verified in main: 50500; WAL entries at the end: 150512.

## 1000000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 11.54 | 15.29 | 47.38 | 47.38 |
| `bulk_update_10000_ms` | 5 | 363.39 | 457.84 | 743.07 | 743.07 |
| `bulk_update_100_ms` | 5 | 6.88 | 8.07 | 16.99 | 16.99 |
| `capture_after_ack_10000_ms` | 5 | 405.93 | 496.49 | 767.42 | 767.42 |
| `capture_after_ack_100_ms` | 5 | 512.52 | 520.13 | 538.44 | 538.44 |
| `checkout_ms` | 10 | 6231.26 | 7512.29 | 10833.40 | 10833.40 |
| `diff_10000_changed_ms` | 15 | 315.13 | 412.30 | 3589.48 | 3589.48 |
| `diff_100_changed_ms` | 15 | 22.04 | 30.37 | 2150.12 | 2150.12 |
| `first_read_ms` | 10 | 2.39 | 5.84 | 11.68 | 11.68 |
| `import_ms` | 1 | 35094.01 | 35094.01 | 35094.01 | 35094.01 |
| `main_checkout_ms` | 1 | 14206.55 | 14206.55 | 14206.55 | 14206.55 |
| `merge_apply_10000_changed_ms` | 5 | 5180.75 | 5272.82 | 5754.78 | 5754.78 |
| `merge_apply_100_changed_ms` | 5 | 47.33 | 55.43 | 2409.13 | 2409.13 |
| `merge_preview_10000_changed_ms` | 5 | 366.41 | 385.01 | 417.67 | 417.67 |
| `merge_preview_100_changed_ms` | 5 | 23.43 | 25.61 | 28.32 | 28.32 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 5581.36 | 5690.49 | 6121.19 | 6121.19 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 72.03 | 81.04 | 2432.56 | 2432.56 |
| `new_branch_to_first_read_ms` | 10 | 6245.66 | 7534.39 | 10881.13 | 10881.13 |
| `point_read_by_id_us` | 1000 | 77.71 | 102.29 | 194.08 | 1455.50 |
| `release_ms` | 10 | 115.79 | 118.85 | 125.21 | 125.21 |
| `sandbox_create_ms` | 5 | 7694.57 | 10759.91 | 12762.29 | 12762.29 |
| `sandbox_create_to_first_read_ms` | 5 | 7699.53 | 10776.09 | 12771.19 | 12771.19 |
| `sandbox_discard_ms` | 5 | 112.03 | 123.44 | 130.68 | 130.68 |
| `sandbox_first_read_ms` | 5 | 4.48 | 8.47 | 14.41 | 14.41 |
| `seed_native_insert_ms` | 1 | 7050.59 | 7050.59 | 7050.59 | 7050.59 |
| `watch_ready_ms` | 10 | 5.44 | 7.79 | 10.10 | 10.10 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 236388890 | 35176448 | 30310400 |
| metadata_after_import | 1000070 | 502280173 | 72740864 | 174944256 |
| main_checkout | 1000000 | 236388890 | 43282432 | 31649792 |
| branch_checkout | 1000000 | 236388890 | 43286528 | 34078720 |
| metadata_at_end | 1050996 | 605057479 | 150745088 | 234459136 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 2823412
- `checkout`: 1791764
- `branch_create`: 27176
- `diff`: 120396
- `merge_preview`: 123416
- `merge_apply`: 1972780
- `release`: 27444
- `branch_delete`: 25636
- `sandbox_create`: 1686776
- `sandbox_discard`: 26612

Merged updates verified in main: 50500; WAL entries at the end: 1050512.
