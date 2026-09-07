# Argon workflow benchmark

Completed 2026-09-07 07:27:30 UTC; duration 134.7 seconds. This is an explicitly sourced local diagnostic build, not a released-version claim. Raw samples, build hashes, environment and configuration: `raw.json`.

Percentiles use nearest rank. With fewer than 100 samples, p99 is usually the observed maximum; these are descriptive observations, not a stable tail-latency estimate. All samples, including first execution, are retained. Scenarios run sequentially; workers run closed-loop within a phase.

Sandbox readiness includes metadata fork, full physical checkout, and acknowledged capture startup. First native query includes a new client connection/handshake and one verified indexed read, after readiness. Capture lag is measured from majority write acknowledgement until a committed WAL record is observed; polling and query latency are included.

Metadata forks reference inherited history. Checked-out sandboxes materialize full physical copies. dbStats logical data bytes, allocated collection bytes, and allocated index bytes are reported separately. Allocations are quantized and can remain after deletion; before/after differences are observations, not a universal per-branch disk price.

## 1000 documents · 1 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.789 | 516.805 | 518.429 | 518.429 |
| divergence_bulk_and_capture_ms | 1 | 83.508 | 83.508 | 83.508 | 83.508 |
| divergence_snapshot_ms | 1 | 29.032 | 29.032 | 29.032 | 29.032 |
| explicit_snapshot_ms | 1 | 26.601 | 26.601 | 26.601 | 26.601 |
| first_native_query_ms | 20 | 10.762 | 13.670 | 14.036 | 14.036 |
| head_materialize_after_snapshot_ms | 20 | 3.073 | 3.258 | 3.443 | 3.443 |
| head_materialize_as_shipped_ms | 20 | 3.945 | 7.574 | 9.275 | 9.275 |
| historical_25pct_ms | 20 | 1.889 | 2.141 | 2.180 | 2.180 |
| historical_50pct_ms | 20 | 2.844 | 3.214 | 3.219 | 3.219 |
| import_ms | 1 | 171.718 | 171.718 | 171.718 | 171.718 |
| metadata_fork_ms | 100 | 19.161 | 24.421 | 28.727 | 29.470 |
| native_write_ack_ms | 20 | 5.454 | 8.917 | 12.205 | 12.205 |
| native_write_to_observed_ms | 20 | 518.470 | 525.675 | 526.997 | 526.997 |
| sandbox_capture_ready_ms | 20 | 154.403 | 181.653 | 211.761 | 211.761 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505093 | 32768 | 77824 |
| metadata after fork samples | 553773 | 32768 | 77824 |
| metadata before divergence | 561080 | 36864 | 81920 |
| metadata after captured divergence | 805270 | 36864 | 81920 |
| metadata after divergent snapshots | 814482 | 36864 | 81920 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 1 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 514.430 | 520.901 | 522.668 | 522.668 |
| divergence_bulk_and_capture_ms | 1 | 63.592 | 63.592 | 63.592 | 63.592 |
| divergence_snapshot_ms | 1 | 30.093 | 30.093 | 30.093 | 30.093 |
| explicit_snapshot_ms | 1 | 22.782 | 22.782 | 22.782 | 22.782 |
| first_native_query_ms | 20 | 10.835 | 12.401 | 14.060 | 14.060 |
| head_materialize_after_snapshot_ms | 20 | 3.273 | 3.638 | 3.820 | 3.820 |
| head_materialize_as_shipped_ms | 20 | 3.813 | 5.606 | 6.981 | 6.981 |
| historical_25pct_ms | 20 | 2.060 | 2.377 | 2.507 | 2.507 |
| historical_50pct_ms | 20 | 3.147 | 3.484 | 3.590 | 3.590 |
| import_ms | 1 | 184.472 | 184.472 | 184.472 | 184.472 |
| metadata_fork_ms | 100 | 15.995 | 21.209 | 24.544 | 25.310 |
| native_write_ack_ms | 20 | 5.351 | 7.006 | 7.067 | 7.067 |
| native_write_to_observed_ms | 20 | 519.912 | 526.251 | 527.434 | 527.434 |
| sandbox_capture_ready_ms | 20 | 165.291 | 182.806 | 183.014 | 183.014 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506548 | 32768 | 77824 |
| metadata after fork samples | 555228 | 32768 | 77824 |
| metadata before divergence | 562535 | 36864 | 86016 |
| metadata after captured divergence | 806725 | 36864 | 86016 |
| metadata after divergent snapshots | 815937 | 36864 | 86016 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 510.347 | 532.307 | 534.652 | 534.652 |
| divergence_bulk_and_capture_ms | 4 | 83.763 | 96.072 | 96.072 | 96.072 |
| divergence_snapshot_ms | 4 | 19.595 | 76.886 | 76.886 | 76.886 |
| explicit_snapshot_ms | 1 | 25.882 | 25.882 | 25.882 | 25.882 |
| first_native_query_ms | 20 | 10.646 | 20.162 | 27.952 | 27.952 |
| head_materialize_after_snapshot_ms | 20 | 3.920 | 4.170 | 4.213 | 4.213 |
| head_materialize_as_shipped_ms | 20 | 6.426 | 8.891 | 8.986 | 8.986 |
| historical_25pct_ms | 20 | 1.983 | 3.109 | 3.158 | 3.158 |
| historical_50pct_ms | 20 | 3.144 | 3.807 | 3.825 | 3.825 |
| import_ms | 1 | 182.830 | 182.830 | 182.830 | 182.830 |
| metadata_fork_ms | 100 | 26.071 | 31.975 | 33.253 | 36.245 |
| native_write_ack_ms | 20 | 7.373 | 24.152 | 25.800 | 25.800 |
| native_write_to_observed_ms | 20 | 520.575 | 538.064 | 540.299 | 540.299 |
| sandbox_capture_ready_ms | 20 | 233.865 | 387.236 | 452.183 | 452.183 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505093 | 32768 | 77824 |
| metadata after fork samples | 553773 | 32768 | 77824 |
| metadata before divergence | 563984 | 36864 | 81920 |
| metadata after captured divergence | 1549767 | 36864 | 81920 |
| metadata after divergent snapshots | 1552091 | 36864 | 81920 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |
| divergent physical copy 1 | 233390 | 8192 | 8192 |
| divergent physical copy 2 | 233390 | 8192 | 8192 |
| divergent physical copy 3 | 233390 | 8192 | 8192 |

Divergence captured **1200** records: **976560 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.398 | 524.318 | 524.346 | 524.346 |
| divergence_bulk_and_capture_ms | 4 | 107.206 | 114.351 | 114.351 | 114.351 |
| divergence_snapshot_ms | 4 | 22.063 | 80.977 | 80.977 | 80.977 |
| explicit_snapshot_ms | 1 | 32.228 | 32.228 | 32.228 | 32.228 |
| first_native_query_ms | 20 | 11.478 | 16.034 | 19.144 | 19.144 |
| head_materialize_after_snapshot_ms | 20 | 4.726 | 7.461 | 7.702 | 7.702 |
| head_materialize_as_shipped_ms | 20 | 4.690 | 5.179 | 5.348 | 5.348 |
| historical_25pct_ms | 20 | 2.398 | 2.946 | 2.953 | 2.953 |
| historical_50pct_ms | 20 | 3.730 | 6.000 | 6.423 | 6.423 |
| import_ms | 1 | 294.130 | 294.130 | 294.130 | 294.130 |
| metadata_fork_ms | 100 | 51.190 | 63.256 | 97.933 | 97.978 |
| native_write_ack_ms | 20 | 9.089 | 27.600 | 27.677 | 27.677 |
| native_write_to_observed_ms | 20 | 525.885 | 545.771 | 545.946 | 545.946 |
| sandbox_capture_ready_ms | 20 | 251.809 | 494.587 | 566.509 | 566.509 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506548 | 32768 | 77824 |
| metadata after fork samples | 555228 | 32768 | 77824 |
| metadata before divergence | 565439 | 36864 | 86016 |
| metadata after captured divergence | 1551406 | 36864 | 86016 |
| metadata after divergent snapshots | 1553546 | 36864 | 86016 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |
| divergent physical copy 1 | 233390 | 8192 | 8192 |
| divergent physical copy 2 | 233390 | 8192 | 8192 |
| divergent physical copy 3 | 233390 | 8192 | 8192 |

Divergence captured **1200** records: **976560 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 514.623 | 520.578 | 520.734 | 520.734 |
| divergence_bulk_and_capture_ms | 1 | 72.826 | 72.826 | 72.826 | 72.826 |
| divergence_snapshot_ms | 1 | 79.954 | 79.954 | 79.954 | 79.954 |
| explicit_snapshot_ms | 1 | 66.090 | 66.090 | 66.090 | 66.090 |
| first_native_query_ms | 20 | 8.526 | 10.980 | 13.499 | 13.499 |
| head_materialize_after_snapshot_ms | 20 | 27.020 | 29.638 | 31.947 | 31.947 |
| head_materialize_as_shipped_ms | 20 | 27.079 | 28.530 | 28.623 | 28.623 |
| historical_25pct_ms | 20 | 11.066 | 11.967 | 12.177 | 12.177 |
| historical_50pct_ms | 20 | 23.151 | 23.915 | 24.016 | 24.016 |
| import_ms | 1 | 547.338 | 547.338 | 547.338 | 547.338 |
| metadata_fork_ms | 100 | 19.966 | 31.377 | 35.025 | 35.510 |
| native_write_ack_ms | 20 | 5.397 | 7.445 | 11.580 | 11.580 |
| native_write_to_observed_ms | 20 | 520.196 | 526.288 | 526.710 | 526.710 |
| sandbox_capture_ready_ms | 20 | 305.526 | 324.371 | 324.543 | 324.543 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010581 | 32768 | 77824 |
| metadata after fork samples | 5059261 | 32768 | 77824 |
| metadata before divergence | 5066568 | 847872 | 1859584 |
| metadata after captured divergence | 5310758 | 847872 | 1859584 |
| metadata after divergent snapshots | 5365958 | 847872 | 1859584 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 514.398 | 544.437 | 546.305 | 546.305 |
| divergence_bulk_and_capture_ms | 1 | 66.463 | 66.463 | 66.463 | 66.463 |
| divergence_snapshot_ms | 1 | 69.060 | 69.060 | 69.060 | 69.060 |
| explicit_snapshot_ms | 1 | 64.349 | 64.349 | 64.349 | 64.349 |
| first_native_query_ms | 20 | 8.950 | 14.179 | 20.784 | 20.784 |
| head_materialize_after_snapshot_ms | 20 | 26.982 | 27.762 | 32.310 | 32.310 |
| head_materialize_as_shipped_ms | 20 | 27.458 | 30.222 | 48.201 | 48.201 |
| historical_25pct_ms | 20 | 12.305 | 12.995 | 13.271 | 13.271 |
| historical_50pct_ms | 20 | 23.452 | 24.198 | 24.524 | 24.524 |
| import_ms | 1 | 552.038 | 552.038 | 552.038 | 552.038 |
| metadata_fork_ms | 100 | 19.063 | 24.632 | 25.863 | 25.984 |
| native_write_ack_ms | 20 | 5.638 | 8.139 | 13.045 | 13.045 |
| native_write_to_observed_ms | 20 | 519.083 | 550.219 | 551.179 | 551.179 |
| sandbox_capture_ready_ms | 20 | 303.455 | 329.055 | 405.209 | 405.209 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012036 | 32768 | 77824 |
| metadata after fork samples | 5060716 | 32768 | 77824 |
| metadata before divergence | 5068023 | 880640 | 1880064 |
| metadata after captured divergence | 5312029 | 880640 | 1880064 |
| metadata after divergent snapshots | 5367413 | 880640 | 1880064 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.253 | 528.270 | 574.346 | 574.346 |
| divergence_bulk_and_capture_ms | 4 | 88.745 | 88.799 | 88.799 | 88.799 |
| divergence_snapshot_ms | 4 | 62.799 | 77.377 | 77.377 | 77.377 |
| explicit_snapshot_ms | 1 | 72.038 | 72.038 | 72.038 | 72.038 |
| first_native_query_ms | 20 | 12.632 | 17.485 | 28.155 | 28.155 |
| head_materialize_after_snapshot_ms | 20 | 29.732 | 33.508 | 33.687 | 33.687 |
| head_materialize_as_shipped_ms | 20 | 31.486 | 46.602 | 47.101 | 47.101 |
| historical_25pct_ms | 20 | 13.822 | 15.515 | 15.599 | 15.599 |
| historical_50pct_ms | 20 | 27.360 | 29.716 | 29.724 | 29.724 |
| import_ms | 1 | 675.321 | 675.321 | 675.321 | 675.321 |
| metadata_fork_ms | 100 | 46.774 | 63.865 | 68.877 | 68.966 |
| native_write_ack_ms | 20 | 7.152 | 9.823 | 11.499 | 11.499 |
| native_write_to_observed_ms | 20 | 518.795 | 533.409 | 582.609 | 582.609 |
| sandbox_capture_ready_ms | 20 | 389.445 | 1144.668 | 1529.793 | 1529.793 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010581 | 32768 | 77824 |
| metadata after fork samples | 5059261 | 32768 | 77824 |
| metadata before divergence | 5069472 | 847872 | 1863680 |
| metadata after captured divergence | 6046232 | 847872 | 1863680 |
| metadata after divergent snapshots | 6103567 | 847872 | 1863680 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |
| divergent physical copy 1 | 2343890 | 8192 | 8192 |
| divergent physical copy 2 | 2343890 | 8192 | 8192 |
| divergent physical copy 3 | 2343890 | 8192 | 8192 |

Divergence captured **1200** records: **976560 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 516.366 | 532.181 | 534.244 | 534.244 |
| divergence_bulk_and_capture_ms | 4 | 98.420 | 101.182 | 101.182 | 101.182 |
| divergence_snapshot_ms | 4 | 65.142 | 129.105 | 129.105 | 129.105 |
| explicit_snapshot_ms | 1 | 69.666 | 69.666 | 69.666 | 69.666 |
| first_native_query_ms | 20 | 13.034 | 16.016 | 19.331 | 19.331 |
| head_materialize_after_snapshot_ms | 20 | 29.774 | 31.609 | 31.995 | 31.995 |
| head_materialize_as_shipped_ms | 20 | 32.354 | 42.227 | 42.786 | 42.786 |
| historical_25pct_ms | 20 | 14.384 | 18.104 | 19.743 | 19.743 |
| historical_50pct_ms | 20 | 26.778 | 29.997 | 30.407 | 30.407 |
| import_ms | 1 | 506.940 | 506.940 | 506.940 | 506.940 |
| metadata_fork_ms | 100 | 25.140 | 28.972 | 31.116 | 33.444 |
| native_write_ack_ms | 20 | 6.213 | 8.450 | 8.471 | 8.471 |
| native_write_to_observed_ms | 20 | 522.579 | 536.481 | 538.515 | 538.515 |
| sandbox_capture_ready_ms | 20 | 344.903 | 753.225 | 974.284 | 974.284 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012036 | 32768 | 77824 |
| metadata after fork samples | 5060716 | 32768 | 77824 |
| metadata before divergence | 5070927 | 847872 | 1863680 |
| metadata after captured divergence | 6047687 | 847872 | 1863680 |
| metadata after divergent snapshots | 6105022 | 847872 | 1863680 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |
| divergent physical copy 1 | 2343890 | 8192 | 8192 |
| divergent physical copy 2 | 2343890 | 8192 | 8192 |
| divergent physical copy 3 | 2343890 | 8192 | 8192 |

Divergence captured **1200** records: **976560 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

