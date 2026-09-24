# Argon workflow benchmark

Completed 2026-09-24 07:50:05 UTC; duration 224.5 seconds. Measured engine source tag `v2.1.2`, commit `03559026972457ea663fdbc77d252e20ffb65b63`. These local measurements are not production latency guarantees. Raw samples, build hashes, environment and configuration: `raw.json`.

Percentiles use nearest rank. With fewer than 100 samples, p99 is usually the observed maximum; these are descriptive observations, not a stable tail-latency estimate. All samples, including first execution, are retained. Scenarios run sequentially; workers run closed-loop within a phase.

Sandbox readiness includes metadata fork, full physical checkout, and acknowledged capture startup. First native query includes a new client connection/handshake and one verified indexed read, after readiness. Capture lag is measured from majority write acknowledgement until a committed WAL record is observed; polling and query latency are included.

Metadata forks reference inherited history. Checked-out sandboxes materialize full physical copies. dbStats logical data bytes, allocated collection bytes, and allocated index bytes are reported separately. Allocations are quantized and can remain after deletion; before/after differences are observations, not a universal per-branch disk price.

## 1000 documents · 1 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 516.264 | 522.468 | 522.778 | 522.778 |
| divergence_bulk_and_capture_ms | 1 | 78.166 | 78.166 | 78.166 | 78.166 |
| divergence_snapshot_ms | 1 | 22.911 | 22.911 | 22.911 | 22.911 |
| explicit_snapshot_ms | 1 | 15.776 | 15.776 | 15.776 | 15.776 |
| first_native_query_ms | 20 | 10.926 | 15.943 | 20.076 | 20.076 |
| head_materialize_after_snapshot_ms | 20 | 1.696 | 1.942 | 2.119 | 2.119 |
| head_materialize_as_shipped_ms | 20 | 3.140 | 4.595 | 4.733 | 4.733 |
| historical_25pct_ms | 20 | 0.902 | 1.231 | 1.232 | 1.232 |
| historical_50pct_ms | 20 | 1.556 | 1.651 | 1.789 | 1.789 |
| import_ms | 1 | 150.193 | 150.193 | 150.193 | 150.193 |
| metadata_fork_ms | 100 | 17.008 | 18.997 | 19.096 | 19.097 |
| native_write_ack_ms | 20 | 5.592 | 6.409 | 7.182 | 7.182 |
| native_write_to_observed_ms | 20 | 520.784 | 528.635 | 529.960 | 529.960 |
| sandbox_capture_ready_ms | 20 | 139.702 | 146.780 | 154.800 | 154.800 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505102 | 32768 | 77824 |
| metadata after fork samples | 553782 | 45056 | 90112 |
| metadata before divergence | 561101 | 204800 | 434176 |
| metadata after captured divergence | 967867 | 204800 | 434176 |
| metadata after divergent snapshots | 977263 | 204800 | 434176 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 1 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 514.470 | 518.710 | 552.941 | 552.941 |
| divergence_bulk_and_capture_ms | 1 | 103.434 | 103.434 | 103.434 | 103.434 |
| divergence_snapshot_ms | 1 | 24.231 | 24.231 | 24.231 | 24.231 |
| explicit_snapshot_ms | 1 | 13.734 | 13.734 | 13.734 | 13.734 |
| first_native_query_ms | 20 | 11.594 | 16.208 | 18.606 | 18.606 |
| head_materialize_after_snapshot_ms | 20 | 1.767 | 1.990 | 2.009 | 2.009 |
| head_materialize_as_shipped_ms | 20 | 3.042 | 5.201 | 5.375 | 5.375 |
| historical_25pct_ms | 20 | 1.046 | 1.274 | 1.318 | 1.318 |
| historical_50pct_ms | 20 | 1.599 | 1.756 | 1.855 | 1.855 |
| import_ms | 1 | 183.990 | 183.990 | 183.990 | 183.990 |
| metadata_fork_ms | 100 | 15.767 | 18.164 | 18.757 | 18.989 |
| native_write_ack_ms | 20 | 5.506 | 7.236 | 14.340 | 14.340 |
| native_write_to_observed_ms | 20 | 519.145 | 525.539 | 559.337 | 559.337 |
| sandbox_capture_ready_ms | 20 | 136.747 | 154.687 | 157.054 | 157.054 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506557 | 32768 | 77824 |
| metadata after fork samples | 555237 | 32768 | 77824 |
| metadata before divergence | 562556 | 208896 | 425984 |
| metadata after captured divergence | 969506 | 208896 | 425984 |
| metadata after divergent snapshots | 978718 | 208896 | 425984 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.349 | 520.220 | 520.481 | 520.481 |
| divergence_bulk_and_capture_ms | 4 | 87.513 | 96.401 | 96.401 | 96.401 |
| divergence_snapshot_ms | 4 | 15.822 | 42.159 | 42.159 | 42.159 |
| explicit_snapshot_ms | 1 | 20.876 | 20.876 | 20.876 | 20.876 |
| first_native_query_ms | 20 | 12.139 | 25.094 | 27.137 | 27.137 |
| head_materialize_after_snapshot_ms | 20 | 3.150 | 3.622 | 3.647 | 3.647 |
| head_materialize_as_shipped_ms | 20 | 4.596 | 5.103 | 5.368 | 5.368 |
| historical_25pct_ms | 20 | 1.584 | 2.198 | 2.285 | 2.285 |
| historical_50pct_ms | 20 | 2.268 | 2.477 | 2.582 | 2.582 |
| import_ms | 1 | 182.601 | 182.601 | 182.601 | 182.601 |
| metadata_fork_ms | 100 | 24.997 | 42.935 | 48.988 | 49.081 |
| native_write_ack_ms | 20 | 6.660 | 21.826 | 26.550 | 26.550 |
| native_write_to_observed_ms | 20 | 519.960 | 540.039 | 542.885 | 542.885 |
| sandbox_capture_ready_ms | 20 | 173.876 | 274.096 | 323.031 | 323.031 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505102 | 32768 | 77824 |
| metadata after fork samples | 553782 | 32768 | 77824 |
| metadata before divergence | 564041 | 196608 | 442368 |
| metadata after captured divergence | 2201179 | 196608 | 442368 |
| metadata after divergent snapshots | 2212279 | 196608 | 442368 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |
| divergent physical copy 1 | 233390 | 8192 | 8192 |
| divergent physical copy 2 | 233390 | 8192 | 8192 |
| divergent physical copy 3 | 233390 | 8192 | 8192 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.247 | 522.561 | 534.364 | 534.364 |
| divergence_bulk_and_capture_ms | 4 | 101.645 | 104.299 | 104.299 | 104.299 |
| divergence_snapshot_ms | 4 | 18.450 | 99.121 | 99.121 | 99.121 |
| explicit_snapshot_ms | 1 | 16.837 | 16.837 | 16.837 | 16.837 |
| first_native_query_ms | 20 | 12.864 | 27.071 | 34.985 | 34.985 |
| head_materialize_after_snapshot_ms | 20 | 2.869 | 3.423 | 3.643 | 3.643 |
| head_materialize_as_shipped_ms | 20 | 4.092 | 9.873 | 10.005 | 10.005 |
| historical_25pct_ms | 20 | 1.464 | 1.935 | 1.973 | 1.973 |
| historical_50pct_ms | 20 | 2.161 | 2.795 | 2.844 | 2.844 |
| import_ms | 1 | 187.857 | 187.857 | 187.857 | 187.857 |
| metadata_fork_ms | 100 | 23.992 | 33.645 | 37.806 | 38.789 |
| native_write_ack_ms | 20 | 5.052 | 10.736 | 17.071 | 17.071 |
| native_write_to_observed_ms | 20 | 519.262 | 531.404 | 539.416 | 539.416 |
| sandbox_capture_ready_ms | 20 | 186.902 | 271.213 | 317.317 | 317.317 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506557 | 32768 | 77824 |
| metadata after fork samples | 555237 | 167936 | 327680 |
| metadata before divergence | 565496 | 221184 | 454656 |
| metadata after captured divergence | 2202634 | 221184 | 454656 |
| metadata after divergent snapshots | 2213734 | 221184 | 454656 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 57344 | 8192 |
| divergent physical copy 1 | 233390 | 53248 | 12288 |
| divergent physical copy 2 | 233390 | 8192 | 8192 |
| divergent physical copy 3 | 233390 | 8192 | 8192 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 518.549 | 528.442 | 548.631 | 548.631 |
| divergence_bulk_and_capture_ms | 1 | 68.726 | 68.726 | 68.726 | 68.726 |
| divergence_snapshot_ms | 1 | 48.390 | 48.390 | 48.390 | 48.390 |
| explicit_snapshot_ms | 1 | 56.525 | 56.525 | 56.525 | 56.525 |
| first_native_query_ms | 20 | 8.480 | 10.693 | 10.824 | 10.824 |
| head_materialize_after_snapshot_ms | 20 | 13.878 | 14.450 | 14.963 | 14.963 |
| head_materialize_as_shipped_ms | 20 | 13.889 | 19.873 | 29.179 | 29.179 |
| historical_25pct_ms | 20 | 6.259 | 6.663 | 6.679 | 6.679 |
| historical_50pct_ms | 20 | 12.303 | 12.716 | 12.768 | 12.768 |
| import_ms | 1 | 375.180 | 375.180 | 375.180 | 375.180 |
| metadata_fork_ms | 100 | 22.014 | 29.998 | 32.015 | 33.001 |
| native_write_ack_ms | 20 | 3.808 | 5.396 | 5.461 | 5.461 |
| native_write_to_observed_ms | 20 | 521.829 | 532.055 | 552.675 | 552.675 |
| sandbox_capture_ready_ms | 20 | 230.937 | 258.275 | 260.345 | 260.345 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010590 | 32768 | 77824 |
| metadata after fork samples | 5059270 | 913408 | 2031616 |
| metadata before divergence | 5066589 | 1073152 | 2301952 |
| metadata after captured divergence | 5473539 | 1073152 | 2301952 |
| metadata after divergent snapshots | 5528739 | 1073152 | 2301952 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 510.532 | 518.881 | 522.590 | 522.590 |
| divergence_bulk_and_capture_ms | 1 | 70.745 | 70.745 | 70.745 | 70.745 |
| divergence_snapshot_ms | 1 | 46.236 | 46.236 | 46.236 | 46.236 |
| explicit_snapshot_ms | 1 | 36.791 | 36.791 | 36.791 | 36.791 |
| first_native_query_ms | 20 | 8.766 | 10.034 | 13.080 | 13.080 |
| head_materialize_after_snapshot_ms | 20 | 13.621 | 13.991 | 14.143 | 14.143 |
| head_materialize_as_shipped_ms | 20 | 13.781 | 16.334 | 20.220 | 20.220 |
| historical_25pct_ms | 20 | 6.367 | 6.853 | 7.218 | 7.218 |
| historical_50pct_ms | 20 | 12.746 | 13.469 | 13.551 | 13.551 |
| import_ms | 1 | 349.179 | 349.179 | 349.179 | 349.179 |
| metadata_fork_ms | 100 | 11.011 | 17.124 | 19.264 | 25.770 |
| native_write_ack_ms | 20 | 4.051 | 4.921 | 5.801 | 5.801 |
| native_write_to_observed_ms | 20 | 514.925 | 523.515 | 526.711 | 526.711 |
| sandbox_capture_ready_ms | 20 | 231.533 | 249.208 | 255.470 | 255.470 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012045 | 32768 | 77824 |
| metadata after fork samples | 5060725 | 843776 | 1855488 |
| metadata before divergence | 5068044 | 974848 | 2019328 |
| metadata after captured divergence | 5474994 | 974848 | 2019328 |
| metadata after divergent snapshots | 5530194 | 974848 | 2019328 |
| one observed checkout (first completed) | 2343890 | 450560 | 307200 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 508.468 | 524.422 | 526.272 | 526.272 |
| divergence_bulk_and_capture_ms | 4 | 102.998 | 118.812 | 118.812 | 118.812 |
| divergence_snapshot_ms | 4 | 37.841 | 44.928 | 44.928 | 44.928 |
| explicit_snapshot_ms | 1 | 37.211 | 37.211 | 37.211 | 37.211 |
| first_native_query_ms | 20 | 6.634 | 13.270 | 14.533 | 14.533 |
| head_materialize_after_snapshot_ms | 20 | 15.804 | 17.765 | 17.963 | 17.963 |
| head_materialize_as_shipped_ms | 20 | 17.498 | 30.145 | 30.733 | 30.733 |
| historical_25pct_ms | 20 | 7.473 | 8.974 | 9.070 | 9.070 |
| historical_50pct_ms | 20 | 14.773 | 16.853 | 17.157 | 17.157 |
| import_ms | 1 | 363.044 | 363.044 | 363.044 | 363.044 |
| metadata_fork_ms | 100 | 21.079 | 33.640 | 42.000 | 42.130 |
| native_write_ack_ms | 20 | 4.239 | 7.187 | 7.367 | 7.367 |
| native_write_to_observed_ms | 20 | 514.353 | 528.913 | 529.139 | 529.139 |
| sandbox_capture_ready_ms | 20 | 331.775 | 474.687 | 605.689 | 605.689 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010590 | 32768 | 77824 |
| metadata after fork samples | 5059270 | 856064 | 1904640 |
| metadata before divergence | 5069529 | 962560 | 1990656 |
| metadata after captured divergence | 6752529 | 962560 | 2035712 |
| metadata after divergent snapshots | 6864822 | 962560 | 2035712 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 581632 | 311296 |
| divergent physical copy 1 | 2343890 | 552960 | 311296 |
| divergent physical copy 2 | 2343890 | 495616 | 315392 |
| divergent physical copy 3 | 2343890 | 491520 | 311296 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 510.336 | 522.281 | 534.432 | 534.432 |
| divergence_bulk_and_capture_ms | 4 | 81.035 | 95.066 | 95.066 | 95.066 |
| divergence_snapshot_ms | 4 | 38.315 | 123.497 | 123.497 | 123.497 |
| explicit_snapshot_ms | 1 | 37.568 | 37.568 | 37.568 | 37.568 |
| first_native_query_ms | 20 | 7.004 | 11.238 | 21.458 | 21.458 |
| head_materialize_after_snapshot_ms | 20 | 16.222 | 18.116 | 18.189 | 18.189 |
| head_materialize_as_shipped_ms | 20 | 18.146 | 26.809 | 27.274 | 27.274 |
| historical_25pct_ms | 20 | 7.856 | 9.290 | 9.325 | 9.325 |
| historical_50pct_ms | 20 | 15.771 | 16.999 | 17.464 | 17.464 |
| import_ms | 1 | 384.918 | 384.918 | 384.918 | 384.918 |
| metadata_fork_ms | 100 | 20.832 | 23.960 | 24.130 | 26.892 |
| native_write_ack_ms | 20 | 4.680 | 6.344 | 6.662 | 6.662 |
| native_write_to_observed_ms | 20 | 516.481 | 525.718 | 539.112 | 539.112 |
| sandbox_capture_ready_ms | 20 | 351.067 | 520.304 | 647.297 | 647.297 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012045 | 32768 | 77824 |
| metadata after fork samples | 5060725 | 851968 | 1843200 |
| metadata before divergence | 5070984 | 974848 | 2035712 |
| metadata after captured divergence | 6698600 | 974848 | 2035712 |
| metadata after divergent snapshots | 6811198 | 974848 | 2035712 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 454656 | 311296 |
| divergent physical copy 1 | 2343890 | 454656 | 311296 |
| divergent physical copy 2 | 2343890 | 458752 | 315392 |
| divergent physical copy 3 | 2343890 | 8192 | 8192 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 1 workers · ancestry depth 1

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 516.514 | 520.598 | 522.711 | 522.711 |
| divergence_bulk_and_capture_ms | 1 | 66.916 | 66.916 | 66.916 | 66.916 |
| divergence_snapshot_ms | 1 | 97.665 | 97.665 | 97.665 | 97.665 |
| explicit_snapshot_ms | 1 | 97.035 | 97.035 | 97.035 | 97.035 |
| first_native_query_ms | 20 | 5.763 | 8.173 | 9.322 | 9.322 |
| head_materialize_after_snapshot_ms | 20 | 27.936 | 30.028 | 30.394 | 30.394 |
| head_materialize_as_shipped_ms | 20 | 27.944 | 36.288 | 66.646 | 66.646 |
| historical_25pct_ms | 20 | 31.698 | 32.390 | 32.977 | 32.977 |
| historical_50pct_ms | 20 | 62.325 | 65.529 | 65.549 | 65.549 |
| import_ms | 1 | 2012.577 | 2012.577 | 2012.577 | 2012.577 |
| metadata_fork_ms | 100 | 16.119 | 18.960 | 19.023 | 19.047 |
| native_write_ack_ms | 20 | 3.796 | 5.383 | 5.573 | 5.573 |
| native_write_to_observed_ms | 20 | 521.456 | 524.274 | 527.399 | 527.399 |
| sandbox_capture_ready_ms | 20 | 581.536 | 597.592 | 603.495 | 603.495 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25075495 | 3244032 | 8486912 |
| metadata after fork samples | 25124175 | 3244032 | 8486912 |
| metadata before divergence | 25131710 | 3964928 | 8859648 |
| metadata after captured divergence | 25538476 | 3964928 | 8859648 |
| metadata after divergent snapshots | 25630495 | 3964928 | 8859648 |
| one observed checkout (first completed) | 11763890 | 1699840 | 1155072 |
| divergent physical copy 0 | 11763890 | 2060288 | 1478656 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 1 workers · ancestry depth 4

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 518.622 | 522.878 | 524.571 | 524.571 |
| divergence_bulk_and_capture_ms | 1 | 71.806 | 71.806 | 71.806 | 71.806 |
| divergence_snapshot_ms | 1 | 105.812 | 105.812 | 105.812 | 105.812 |
| explicit_snapshot_ms | 1 | 98.272 | 98.272 | 98.272 | 98.272 |
| first_native_query_ms | 20 | 5.798 | 8.150 | 9.462 | 9.462 |
| head_materialize_after_snapshot_ms | 20 | 28.342 | 30.434 | 31.610 | 31.610 |
| head_materialize_as_shipped_ms | 20 | 28.048 | 29.828 | 29.911 | 29.911 |
| historical_25pct_ms | 20 | 31.922 | 32.421 | 32.561 | 32.561 |
| historical_50pct_ms | 20 | 63.864 | 65.627 | 65.635 | 65.635 |
| import_ms | 1 | 1386.141 | 1386.141 | 1386.141 | 1386.141 |
| metadata_fork_ms | 100 | 16.056 | 18.944 | 18.978 | 22.900 |
| native_write_ack_ms | 20 | 4.220 | 5.575 | 6.113 | 6.113 |
| native_write_to_observed_ms | 20 | 522.480 | 528.873 | 529.034 | 529.034 |
| sandbox_capture_ready_ms | 20 | 599.106 | 646.289 | 761.975 | 761.975 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25076950 | 3653632 | 8679424 |
| metadata after fork samples | 25125630 | 3653632 | 8679424 |
| metadata before divergence | 25133165 | 4091904 | 9105408 |
| metadata after captured divergence | 25540115 | 4091904 | 9129984 |
| metadata after divergent snapshots | 25631950 | 4145152 | 9158656 |
| one observed checkout (first completed) | 11763890 | 1921024 | 1261568 |
| divergent physical copy 0 | 11763890 | 2256896 | 1486848 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 4 workers · ancestry depth 1

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 508.736 | 518.212 | 528.501 | 528.501 |
| divergence_bulk_and_capture_ms | 4 | 106.414 | 113.724 | 113.724 | 113.724 |
| divergence_snapshot_ms | 4 | 95.152 | 151.257 | 151.257 | 151.257 |
| explicit_snapshot_ms | 1 | 101.056 | 101.056 | 101.056 | 101.056 |
| first_native_query_ms | 20 | 9.873 | 16.109 | 16.381 | 16.381 |
| head_materialize_after_snapshot_ms | 20 | 60.494 | 73.251 | 78.775 | 78.775 |
| head_materialize_as_shipped_ms | 20 | 63.697 | 103.932 | 118.770 | 118.770 |
| historical_25pct_ms | 20 | 39.956 | 41.598 | 41.779 | 41.779 |
| historical_50pct_ms | 20 | 76.670 | 79.176 | 79.596 | 79.596 |
| import_ms | 1 | 1415.152 | 1415.152 | 1415.152 | 1415.152 |
| metadata_fork_ms | 100 | 20.933 | 23.014 | 23.596 | 26.629 |
| native_write_ack_ms | 20 | 4.848 | 6.439 | 6.741 | 6.741 |
| native_write_to_observed_ms | 20 | 514.889 | 523.059 | 531.098 | 531.098 |
| sandbox_capture_ready_ms | 20 | 1410.856 | 1616.044 | 2132.148 | 2132.148 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25075495 | 3452928 | 8183808 |
| metadata after fork samples | 25124175 | 3551232 | 8183808 |
| metadata before divergence | 25134650 | 3985408 | 8826880 |
| metadata after captured divergence | 26762266 | 3985408 | 8826880 |
| metadata after divergent snapshots | 26949430 | 3985408 | 8990720 |
| one observed checkout (first completed) | 11763890 | 1658880 | 1212416 |
| divergent physical copy 0 | 11763890 | 2277376 | 1548288 |
| divergent physical copy 1 | 11763890 | 2260992 | 1527808 |
| divergent physical copy 2 | 11763890 | 2289664 | 1585152 |
| divergent physical copy 3 | 11763890 | 2265088 | 1699840 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 4 workers · ancestry depth 4

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 510.283 | 518.611 | 524.155 | 524.155 |
| divergence_bulk_and_capture_ms | 4 | 93.281 | 96.163 | 96.163 | 96.163 |
| divergence_snapshot_ms | 4 | 96.291 | 179.839 | 179.839 | 179.839 |
| explicit_snapshot_ms | 1 | 103.860 | 103.860 | 103.860 | 103.860 |
| first_native_query_ms | 20 | 8.460 | 20.004 | 22.290 | 22.290 |
| head_materialize_after_snapshot_ms | 20 | 59.018 | 71.041 | 76.974 | 76.974 |
| head_materialize_as_shipped_ms | 20 | 66.421 | 73.082 | 78.214 | 78.214 |
| historical_25pct_ms | 20 | 39.493 | 42.252 | 42.301 | 42.301 |
| historical_50pct_ms | 20 | 82.556 | 87.999 | 89.822 | 89.822 |
| import_ms | 1 | 1349.188 | 1349.188 | 1349.188 | 1349.188 |
| metadata_fork_ms | 100 | 17.873 | 28.928 | 35.884 | 35.924 |
| native_write_ack_ms | 20 | 4.838 | 6.220 | 9.048 | 9.048 |
| native_write_to_observed_ms | 20 | 515.534 | 524.321 | 529.453 | 529.453 |
| sandbox_capture_ready_ms | 20 | 1425.893 | 1599.132 | 2122.075 | 2122.075 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25076950 | 3653632 | 8667136 |
| metadata after fork samples | 25125630 | 3653632 | 8667136 |
| metadata before divergence | 25136105 | 3993600 | 8835072 |
| metadata after captured divergence | 26763721 | 3993600 | 8835072 |
| metadata after divergent snapshots | 26950885 | 4157440 | 9158656 |
| one observed checkout (first completed) | 11763890 | 1646592 | 1638400 |
| divergent physical copy 0 | 11763890 | 2289664 | 1560576 |
| divergent physical copy 1 | 11763890 | 2281472 | 1605632 |
| divergent physical copy 2 | 11763890 | 2256896 | 1576960 |
| divergent physical copy 3 | 11763890 | 2260992 | 1650688 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

