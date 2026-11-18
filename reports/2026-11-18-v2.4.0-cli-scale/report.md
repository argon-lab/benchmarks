# Argon 2.4.0 CLI workflow at 10000, 100000, 1000000 documents

Window: `2026-11-18T02:17:52Z` → `2026-11-18T02:28:16Z`. Complete: **True**.

Binary SHA256 `7da8a5b960a9985bf8f4c71fa235cdc0212dc80ed9c51e1e6fea8b9350ff3cff`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs and 13.6 GiB visible to the measuring process.

Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; with few samples the maximum is the observed maximum, not a tail estimate.

## 10000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 12.04 | 14.87 | 44.48 | 44.48 |
| `bulk_update_10000_ms` | 5 | 142.37 | 150.92 | 215.87 | 215.87 |
| `bulk_update_100_ms` | 5 | 2.57 | 3.04 | 3.70 | 3.70 |
| `capture_after_ack_10000_ms` | 5 | 256.62 | 282.84 | 304.88 | 304.88 |
| `capture_after_ack_100_ms` | 5 | 519.84 | 524.06 | 539.16 | 539.16 |
| `checkout_ms` | 10 | 70.84 | 77.89 | 85.03 | 85.03 |
| `diff_10000_changed_ms` | 15 | 146.22 | 178.50 | 228.90 | 228.90 |
| `diff_100_changed_ms` | 15 | 85.01 | 100.83 | 157.36 | 157.36 |
| `first_read_ms` | 10 | 1.39 | 1.58 | 3.10 | 3.10 |
| `import_ms` | 1 | 200.71 | 200.71 | 200.71 | 200.71 |
| `main_checkout_ms` | 1 | 78.23 | 78.23 | 78.23 | 78.23 |
| `merge_apply_10000_changed_ms` | 5 | 1874.80 | 1951.90 | 2382.86 | 2382.86 |
| `merge_apply_100_changed_ms` | 5 | 34.02 | 42.26 | 74.28 | 74.28 |
| `merge_preview_10000_changed_ms` | 5 | 206.60 | 225.34 | 286.83 | 286.83 |
| `merge_preview_100_changed_ms` | 5 | 83.55 | 99.32 | 104.28 | 104.28 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 2096.17 | 2177.23 | 2669.69 | 2669.69 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 117.57 | 141.62 | 173.60 | 173.60 |
| `new_branch_to_first_read_ms` | 10 | 87.82 | 96.37 | 133.02 | 133.02 |
| `point_read_by_id_us` | 1000 | 66.83 | 77.88 | 96.50 | 137.62 |
| `release_ms` | 10 | 112.58 | 118.46 | 143.97 | 143.97 |
| `sandbox_create_ms` | 5 | 100.01 | 111.13 | 150.82 | 150.82 |
| `sandbox_create_to_first_read_ms` | 5 | 101.69 | 113.94 | 153.60 | 153.60 |
| `sandbox_discard_ms` | 5 | 111.52 | 114.93 | 133.27 | 133.27 |
| `sandbox_first_read_ms` | 5 | 1.52 | 2.44 | 4.11 | 4.11 |
| `seed_native_insert_ms` | 1 | 43.82 | 43.82 | 43.82 | 43.82 |
| `watch_ready_ms` | 10 | 4.49 | 5.10 | 8.14 | 8.14 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 2343890 | 4096 | 4096 |
| metadata_after_import | 10007 | 5010089 | 32768 | 77824 |
| main_checkout | 10000 | 2343890 | 4096 | 4096 |
| branch_checkout | 10000 | 2343890 | 4096 | 4096 |
| metadata_at_end | 60555 | 77548365 | 19578880 | 21057536 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 55164
- `checkout`: 48560
- `branch_create`: 27032
- `diff`: 115048
- `merge_preview`: 135592
- `merge_apply`: 141140
- `release`: 27232
- `branch_delete`: 26760
- `sandbox_create`: 50496
- `sandbox_discard`: 26648

Merged updates verified in main: 50500; WAL entries at the end: 60512.

## 100000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 12.85 | 15.71 | 38.41 | 38.41 |
| `bulk_update_10000_ms` | 5 | 158.46 | 167.51 | 318.57 | 318.57 |
| `bulk_update_100_ms` | 5 | 2.68 | 3.29 | 4.00 | 4.00 |
| `capture_after_ack_10000_ms` | 5 | 290.50 | 334.62 | 382.41 | 382.41 |
| `capture_after_ack_100_ms` | 5 | 515.99 | 536.67 | 538.08 | 538.08 |
| `checkout_ms` | 10 | 520.26 | 567.50 | 612.05 | 612.05 |
| `diff_10000_changed_ms` | 15 | 421.21 | 616.70 | 1202.65 | 1202.65 |
| `diff_100_changed_ms` | 15 | 326.62 | 348.44 | 676.07 | 676.07 |
| `first_read_ms` | 10 | 1.45 | 1.72 | 4.17 | 4.17 |
| `import_ms` | 1 | 1883.74 | 1883.74 | 1883.74 | 1883.74 |
| `main_checkout_ms` | 1 | 615.63 | 615.63 | 615.63 | 615.63 |
| `merge_apply_10000_changed_ms` | 5 | 2062.22 | 2163.69 | 2795.22 | 2795.22 |
| `merge_apply_100_changed_ms` | 5 | 37.50 | 38.83 | 240.13 | 240.13 |
| `merge_preview_10000_changed_ms` | 5 | 482.69 | 516.27 | 693.38 | 693.38 |
| `merge_preview_100_changed_ms` | 5 | 335.09 | 350.59 | 362.38 | 362.38 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 2544.90 | 2679.97 | 3343.04 | 3343.04 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 373.92 | 392.70 | 593.23 | 593.23 |
| `new_branch_to_first_read_ms` | 10 | 534.89 | 583.63 | 649.04 | 649.04 |
| `point_read_by_id_us` | 1000 | 70.21 | 80.88 | 111.71 | 265.25 |
| `release_ms` | 10 | 112.25 | 117.29 | 137.70 | 137.70 |
| `sandbox_create_ms` | 5 | 818.24 | 845.46 | 984.63 | 984.63 |
| `sandbox_create_to_first_read_ms` | 5 | 820.25 | 852.11 | 986.58 | 986.58 |
| `sandbox_discard_ms` | 5 | 110.32 | 116.19 | 124.76 | 124.76 |
| `sandbox_first_read_ms` | 5 | 1.73 | 2.50 | 6.14 | 6.14 |
| `seed_native_insert_ms` | 1 | 397.25 | 397.25 | 397.25 | 397.25 |
| `watch_ready_ms` | 10 | 4.66 | 5.67 | 10.49 | 10.49 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 23538890 | 4096 | 4096 |
| metadata_after_import | 100013 | 50142727 | 6332416 | 15814656 |
| main_checkout | 100000 | 23538890 | 3530752 | 2273280 |
| branch_checkout | 100000 | 23538890 | 4096 | 1216512 |
| metadata_at_end | 150597 | 125915197 | 38182912 | 44924928 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 299588
- `checkout`: 208564
- `branch_create`: 25168
- `diff`: 554260
- `merge_preview`: 548376
- `merge_apply`: 320940
- `release`: 27196
- `branch_delete`: 26724
- `sandbox_create`: 206748
- `sandbox_discard`: 25580

Merged updates verified in main: 50500; WAL entries at the end: 150512.

## 1000000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 14.43 | 21.41 | 57.71 | 57.71 |
| `bulk_update_10000_ms` | 5 | 424.52 | 819.61 | 1115.15 | 1115.15 |
| `bulk_update_100_ms` | 5 | 6.75 | 7.16 | 11.48 | 11.48 |
| `capture_after_ack_10000_ms` | 5 | 313.39 | 528.14 | 763.42 | 763.42 |
| `capture_after_ack_100_ms` | 5 | 513.51 | 519.93 | 528.75 | 528.75 |
| `checkout_ms` | 10 | 6762.61 | 8410.77 | 10892.39 | 10892.39 |
| `diff_10000_changed_ms` | 15 | 5011.01 | 8491.08 | 20606.52 | 20606.52 |
| `diff_100_changed_ms` | 15 | 4816.46 | 7087.62 | 14907.24 | 14907.24 |
| `first_read_ms` | 10 | 2.96 | 5.58 | 14.59 | 14.59 |
| `import_ms` | 1 | 28377.39 | 28377.39 | 28377.39 | 28377.39 |
| `main_checkout_ms` | 1 | 7027.25 | 7027.25 | 7027.25 | 7027.25 |
| `merge_apply_10000_changed_ms` | 5 | 5499.12 | 6420.68 | 7814.27 | 7814.27 |
| `merge_apply_100_changed_ms` | 5 | 78.88 | 111.95 | 3101.06 | 3101.06 |
| `merge_preview_10000_changed_ms` | 5 | 5071.67 | 6180.19 | 7349.05 | 7349.05 |
| `merge_preview_100_changed_ms` | 5 | 5141.16 | 6045.03 | 8425.35 | 8425.35 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 10570.80 | 12596.90 | 15163.31 | 15163.31 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 5220.04 | 6133.94 | 11526.41 | 11526.41 |
| `new_branch_to_first_read_ms` | 10 | 6794.75 | 8472.49 | 10959.84 | 10959.84 |
| `point_read_by_id_us` | 1000 | 77.71 | 129.17 | 262.29 | 7017.04 |
| `release_ms` | 10 | 116.66 | 122.43 | 148.09 | 148.09 |
| `sandbox_create_ms` | 5 | 6989.97 | 7772.39 | 8411.16 | 8411.16 |
| `sandbox_create_to_first_read_ms` | 5 | 6992.86 | 7776.04 | 8415.17 | 8415.17 |
| `sandbox_discard_ms` | 5 | 109.25 | 115.74 | 120.44 | 120.44 |
| `sandbox_first_read_ms` | 5 | 2.44 | 2.79 | 3.38 | 3.38 |
| `seed_native_insert_ms` | 1 | 6095.49 | 6095.49 | 6095.49 | 6095.49 |
| `watch_ready_ms` | 10 | 5.41 | 8.03 | 13.37 | 13.37 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 1000000 | 236388890 | 35053568 | 29626368 |
| metadata_after_import | 1000070 | 502280173 | 72105984 | 175751168 |
| main_checkout | 1000000 | 236388890 | 43659264 | 31449088 |
| branch_checkout | 1000000 | 236388890 | 40144896 | 30560256 |
| metadata_at_end | 1050996 | 605057379 | 156135424 | 233299968 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 2355092
- `checkout`: 1685360
- `branch_create`: 27132
- `diff`: 5136660
- `merge_preview`: 4976324
- `merge_apply`: 2026324
- `release`: 27180
- `branch_delete`: 24660
- `sandbox_create`: 1814684
- `sandbox_discard`: 26788

Merged updates verified in main: 50500; WAL entries at the end: 1050512.
