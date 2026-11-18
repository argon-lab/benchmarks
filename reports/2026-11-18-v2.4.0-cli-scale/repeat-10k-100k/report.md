# Argon 2.4.0 CLI workflow at 10000, 100000 documents

Window: `2026-11-18T02:30:33Z` → `2026-11-18T02:31:48Z`. Complete: **True**.

Binary SHA256 `7da8a5b960a9985bf8f4c71fa235cdc0212dc80ed9c51e1e6fea8b9350ff3cff`; MongoDB 7.0.45; WiredTiger cache 2.00 GiB; 12 logical CPUs and 13.6 GiB visible to the measuring process.

Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; with few samples the maximum is the observed maximum, not a tail estimate.

## 10000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 11.86 | 16.65 | 38.11 | 38.11 |
| `bulk_update_10000_ms` | 5 | 143.95 | 146.02 | 180.39 | 180.39 |
| `bulk_update_100_ms` | 5 | 2.53 | 4.47 | 5.60 | 5.60 |
| `capture_after_ack_10000_ms` | 5 | 257.42 | 273.05 | 283.70 | 283.70 |
| `capture_after_ack_100_ms` | 5 | 519.33 | 529.03 | 535.49 | 535.49 |
| `checkout_ms` | 10 | 68.14 | 70.38 | 80.79 | 80.79 |
| `diff_10000_changed_ms` | 15 | 117.86 | 144.74 | 223.69 | 223.69 |
| `diff_100_changed_ms` | 15 | 80.49 | 90.45 | 141.14 | 141.14 |
| `first_read_ms` | 10 | 1.36 | 1.46 | 1.95 | 1.95 |
| `import_ms` | 1 | 208.92 | 208.92 | 208.92 | 208.92 |
| `main_checkout_ms` | 1 | 70.42 | 70.42 | 70.42 | 70.42 |
| `merge_apply_10000_changed_ms` | 5 | 1798.44 | 1816.26 | 1826.92 | 1826.92 |
| `merge_apply_100_changed_ms` | 5 | 33.67 | 36.62 | 65.90 | 65.90 |
| `merge_preview_10000_changed_ms` | 5 | 144.76 | 176.14 | 184.43 | 184.43 |
| `merge_preview_100_changed_ms` | 5 | 81.35 | 88.98 | 105.52 | 105.52 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 1962.45 | 1974.58 | 2005.89 | 2005.89 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 115.02 | 123.37 | 157.55 | 157.55 |
| `new_branch_to_first_read_ms` | 10 | 81.91 | 96.15 | 116.43 | 116.43 |
| `point_read_by_id_us` | 1000 | 67.75 | 82.00 | 92.67 | 161.96 |
| `release_ms` | 10 | 109.89 | 117.60 | 131.05 | 131.05 |
| `sandbox_create_ms` | 5 | 93.30 | 97.24 | 104.89 | 104.89 |
| `sandbox_create_to_first_read_ms` | 5 | 94.92 | 98.81 | 106.78 | 106.78 |
| `sandbox_discard_ms` | 5 | 109.23 | 110.68 | 112.51 | 112.51 |
| `sandbox_first_read_ms` | 5 | 1.35 | 1.47 | 1.71 | 1.71 |
| `seed_native_insert_ms` | 1 | 48.56 | 48.56 | 48.56 | 48.56 |
| `watch_ready_ms` | 10 | 4.47 | 4.80 | 12.14 | 12.14 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 10000 | 2343890 | 4096 | 4096 |
| metadata_after_import | 10007 | 5010089 | 32768 | 77824 |
| main_checkout | 10000 | 2343890 | 4096 | 4096 |
| branch_checkout | 10000 | 2343890 | 4096 | 4096 |
| metadata_at_end | 60555 | 77568565 | 18886656 | 21254144 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 69308
- `checkout`: 50636
- `branch_create`: 27024
- `diff`: 114396
- `merge_preview`: 125156
- `merge_apply`: 147388
- `release`: 27212
- `branch_delete`: 26740
- `sandbox_create`: 48756
- `sandbox_discard`: 24508

Merged updates verified in main: 50500; WAL entries at the end: 60512.

## 100000 documents

| Operation | n | min | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| `branch_create_ms` | 10 | 12.32 | 13.06 | 37.65 | 37.65 |
| `bulk_update_10000_ms` | 5 | 156.85 | 172.61 | 259.61 | 259.61 |
| `bulk_update_100_ms` | 5 | 3.05 | 3.32 | 3.72 | 3.72 |
| `capture_after_ack_10000_ms` | 5 | 315.49 | 379.65 | 397.26 | 397.26 |
| `capture_after_ack_100_ms` | 5 | 522.70 | 528.80 | 544.09 | 544.09 |
| `checkout_ms` | 10 | 565.91 | 586.38 | 661.70 | 661.70 |
| `diff_10000_changed_ms` | 15 | 427.13 | 473.42 | 763.72 | 763.72 |
| `diff_100_changed_ms` | 15 | 341.92 | 369.67 | 570.28 | 570.28 |
| `first_read_ms` | 10 | 1.46 | 1.61 | 2.84 | 2.84 |
| `import_ms` | 1 | 1566.79 | 1566.79 | 1566.79 | 1566.79 |
| `main_checkout_ms` | 1 | 561.48 | 561.48 | 561.48 | 561.48 |
| `merge_apply_10000_changed_ms` | 5 | 2045.27 | 2133.59 | 2335.71 | 2335.71 |
| `merge_apply_100_changed_ms` | 5 | 34.80 | 38.96 | 244.37 | 244.37 |
| `merge_preview_10000_changed_ms` | 5 | 476.47 | 482.45 | 641.81 | 641.81 |
| `merge_preview_100_changed_ms` | 5 | 348.08 | 366.54 | 435.05 | 435.05 |
| `merge_preview_plus_apply_10000_changed_ms` | 5 | 2526.76 | 2622.02 | 2868.17 | 2868.17 |
| `merge_preview_plus_apply_100_changed_ms` | 5 | 383.19 | 418.35 | 594.34 | 594.34 |
| `new_branch_to_first_read_ms` | 10 | 593.89 | 606.48 | 677.17 | 677.17 |
| `point_read_by_id_us` | 1000 | 66.83 | 83.42 | 91.92 | 145.79 |
| `release_ms` | 10 | 111.90 | 113.55 | 125.44 | 125.44 |
| `sandbox_create_ms` | 5 | 592.11 | 598.34 | 614.68 | 614.68 |
| `sandbox_create_to_first_read_ms` | 5 | 593.80 | 601.22 | 616.39 | 616.39 |
| `sandbox_discard_ms` | 5 | 109.39 | 114.30 | 114.70 | 114.70 |
| `sandbox_first_read_ms` | 5 | 1.38 | 1.50 | 2.63 | 2.63 |
| `seed_native_insert_ms` | 1 | 367.32 | 367.32 | 367.32 | 367.32 |
| `watch_ready_ms` | 10 | 4.41 | 4.65 | 5.36 | 5.36 |

| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |
|---|---:|---:|---:|---:|
| source | 100000 | 23538890 | 4096 | 4096 |
| metadata_after_import | 100013 | 50142727 | 7213056 | 13672448 |
| main_checkout | 100000 | 23538890 | 4096 | 1347584 |
| branch_checkout | 100000 | 23538890 | 2355200 | 1417216 |
| metadata_at_end | 150597 | 125905097 | 38006784 | 44552192 |

Largest peak resident memory of one CLI process, by command (kB):

- `import`: 282068
- `checkout`: 207504
- `branch_create`: 26340
- `diff`: 572552
- `merge_preview`: 569356
- `merge_apply`: 319320
- `release`: 27308
- `branch_delete`: 26756
- `sandbox_create`: 213144
- `sandbox_discard`: 26744

Merged updates verified in main: 50500; WAL entries at the end: 150512.
