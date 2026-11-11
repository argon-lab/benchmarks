# Argon workflow benchmark

Completed 2026-11-11 11:16:30 UTC; duration 188.3 seconds. Measured engine source tag `v2.1.5`, commit `e1172b0672b797b4c528005023a5364504882a9b`. These local measurements are not production latency guarantees. Raw samples, build hashes, environment and configuration: `raw.json`.

Percentiles use nearest rank. With fewer than 100 samples, p99 is usually the observed maximum; these are descriptive observations, not a stable tail-latency estimate. All samples, including first execution, are retained. Scenarios run sequentially; workers run closed-loop within a phase.

Sandbox readiness includes metadata fork, full physical checkout, and acknowledged capture startup. First native query includes a new client connection/handshake and one verified indexed read, after readiness. Capture lag is measured from majority write acknowledgement until a committed WAL record is observed; polling and query latency are included.

Metadata forks reference inherited history. Checked-out sandboxes materialize full physical copies. dbStats logical data bytes, allocated collection bytes, and allocated index bytes are reported separately. Allocations are quantized and can remain after deletion; before/after differences are observations, not a universal per-branch disk price.

## 1000 documents · 1 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.396 | 508.447 | 558.557 | 558.557 |
| divergence_bulk_and_capture_ms | 1 | 39.473 | 39.473 | 39.473 | 39.473 |
| divergence_snapshot_ms | 1 | 18.487 | 18.487 | 18.487 | 18.487 |
| explicit_snapshot_ms | 1 | 9.560 | 9.560 | 9.560 | 9.560 |
| first_native_query_ms | 20 | 1.751 | 1.930 | 1.976 | 1.976 |
| head_materialize_after_snapshot_ms | 20 | 2.483 | 3.365 | 3.877 | 3.877 |
| head_materialize_as_shipped_ms | 20 | 4.584 | 7.041 | 7.396 | 7.396 |
| historical_25pct_ms | 20 | 2.118 | 2.490 | 3.586 | 3.586 |
| historical_50pct_ms | 20 | 3.339 | 5.522 | 6.200 | 6.200 |
| import_ms | 1 | 70.643 | 70.643 | 70.643 | 70.643 |
| metadata_fork_ms | 100 | 3.526 | 5.049 | 5.817 | 5.955 |
| native_write_ack_ms | 20 | 0.939 | 1.589 | 1.598 | 1.598 |
| native_write_to_observed_ms | 20 | 507.432 | 510.037 | 559.228 | 559.228 |
| sandbox_capture_ready_ms | 20 | 51.341 | 62.436 | 65.261 | 65.261 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505102 | 32768 | 77824 |
| metadata after fork samples | 553782 | 32768 | 77824 |
| metadata before divergence | 561101 | 204800 | 434176 |
| metadata after captured divergence | 968051 | 204800 | 434176 |
| metadata after divergent snapshots | 977263 | 204800 | 434176 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 1 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.440 | 508.815 | 510.578 | 510.578 |
| divergence_bulk_and_capture_ms | 1 | 38.435 | 38.435 | 38.435 | 38.435 |
| divergence_snapshot_ms | 1 | 22.544 | 22.544 | 22.544 | 22.544 |
| explicit_snapshot_ms | 1 | 9.915 | 9.915 | 9.915 | 9.915 |
| first_native_query_ms | 20 | 1.884 | 2.594 | 2.618 | 2.618 |
| head_materialize_after_snapshot_ms | 20 | 3.301 | 4.449 | 4.531 | 4.531 |
| head_materialize_as_shipped_ms | 20 | 4.347 | 6.594 | 11.101 | 11.101 |
| historical_25pct_ms | 20 | 3.237 | 5.118 | 5.716 | 5.716 |
| historical_50pct_ms | 20 | 4.808 | 6.845 | 6.982 | 6.982 |
| import_ms | 1 | 72.583 | 72.583 | 72.583 | 72.583 |
| metadata_fork_ms | 100 | 3.732 | 4.907 | 5.115 | 5.858 |
| native_write_ack_ms | 20 | 1.308 | 1.669 | 1.710 | 1.710 |
| native_write_to_observed_ms | 20 | 507.625 | 509.876 | 511.454 | 511.454 |
| sandbox_capture_ready_ms | 20 | 52.276 | 66.594 | 70.895 | 70.895 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506557 | 32768 | 77824 |
| metadata after fork samples | 555237 | 32768 | 77824 |
| metadata before divergence | 562556 | 364544 | 831488 |
| metadata after captured divergence | 969506 | 364544 | 831488 |
| metadata after divergent snapshots | 978900 | 364544 | 831488 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.652 | 508.332 | 508.534 | 508.534 |
| divergence_bulk_and_capture_ms | 4 | 52.537 | 59.520 | 59.520 | 59.520 |
| divergence_snapshot_ms | 4 | 10.370 | 16.578 | 16.578 | 16.578 |
| explicit_snapshot_ms | 1 | 15.083 | 15.083 | 15.083 | 15.083 |
| first_native_query_ms | 20 | 1.874 | 2.495 | 4.438 | 4.438 |
| head_materialize_after_snapshot_ms | 20 | 2.542 | 4.483 | 4.682 | 4.682 |
| head_materialize_as_shipped_ms | 20 | 6.420 | 8.521 | 8.563 | 8.563 |
| historical_25pct_ms | 20 | 2.926 | 4.276 | 4.455 | 4.455 |
| historical_50pct_ms | 20 | 5.018 | 6.226 | 7.238 | 7.238 |
| import_ms | 1 | 69.722 | 69.722 | 69.722 | 69.722 |
| metadata_fork_ms | 100 | 3.041 | 4.285 | 5.065 | 5.148 |
| native_write_ack_ms | 20 | 1.282 | 2.235 | 3.451 | 3.451 |
| native_write_to_observed_ms | 20 | 506.306 | 509.817 | 509.829 | 509.829 |
| sandbox_capture_ready_ms | 20 | 56.644 | 82.510 | 96.972 | 96.972 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505102 | 32768 | 77824 |
| metadata after fork samples | 553782 | 32768 | 77824 |
| metadata before divergence | 564039 | 204800 | 454656 |
| metadata after captured divergence | 2191839 | 204800 | 454656 |
| metadata after divergent snapshots | 2212461 | 204800 | 454656 |
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
| capture_ack_to_observed_ms | 20 | 506.333 | 508.356 | 508.548 | 508.548 |
| divergence_bulk_and_capture_ms | 4 | 59.025 | 60.601 | 60.601 | 60.601 |
| divergence_snapshot_ms | 4 | 18.442 | 23.702 | 23.702 | 23.702 |
| explicit_snapshot_ms | 1 | 9.966 | 9.966 | 9.966 | 9.966 |
| first_native_query_ms | 20 | 1.896 | 3.071 | 7.533 | 7.533 |
| head_materialize_after_snapshot_ms | 20 | 3.505 | 4.114 | 4.399 | 4.399 |
| head_materialize_as_shipped_ms | 20 | 5.662 | 10.836 | 11.026 | 11.026 |
| historical_25pct_ms | 20 | 4.515 | 6.220 | 6.609 | 6.609 |
| historical_50pct_ms | 20 | 6.778 | 8.414 | 8.763 | 8.763 |
| import_ms | 1 | 69.246 | 69.246 | 69.246 | 69.246 |
| metadata_fork_ms | 100 | 3.501 | 5.205 | 5.807 | 5.870 |
| native_write_ack_ms | 20 | 1.410 | 2.483 | 3.119 | 3.119 |
| native_write_to_observed_ms | 20 | 507.686 | 509.652 | 510.629 | 510.629 |
| sandbox_capture_ready_ms | 20 | 52.540 | 88.577 | 104.798 | 104.798 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506557 | 32768 | 77824 |
| metadata after fork samples | 555237 | 32768 | 77824 |
| metadata before divergence | 565496 | 192512 | 421888 |
| metadata after captured divergence | 2193296 | 192512 | 421888 |
| metadata after divergent snapshots | 2213734 | 192512 | 421888 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 57344 | 40960 |
| divergent physical copy 1 | 233390 | 57344 | 40960 |
| divergent physical copy 2 | 233390 | 8192 | 8192 |
| divergent physical copy 3 | 233390 | 8192 | 8192 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.891 | 510.464 | 510.502 | 510.502 |
| divergence_bulk_and_capture_ms | 1 | 45.324 | 45.324 | 45.324 | 45.324 |
| divergence_snapshot_ms | 1 | 67.495 | 67.495 | 67.495 | 67.495 |
| explicit_snapshot_ms | 1 | 33.768 | 33.768 | 33.768 | 33.768 |
| first_native_query_ms | 20 | 1.830 | 2.870 | 3.380 | 3.380 |
| head_materialize_after_snapshot_ms | 20 | 16.229 | 17.455 | 18.805 | 18.805 |
| head_materialize_as_shipped_ms | 20 | 17.134 | 20.765 | 36.841 | 36.841 |
| historical_25pct_ms | 20 | 12.667 | 15.108 | 15.198 | 15.198 |
| historical_50pct_ms | 20 | 23.079 | 26.552 | 26.817 | 26.817 |
| import_ms | 1 | 346.773 | 346.773 | 346.773 | 346.773 |
| metadata_fork_ms | 100 | 3.729 | 5.029 | 5.885 | 6.538 |
| native_write_ack_ms | 20 | 1.325 | 1.928 | 2.113 | 2.113 |
| native_write_to_observed_ms | 20 | 506.215 | 512.187 | 512.430 | 512.430 |
| sandbox_capture_ready_ms | 20 | 150.651 | 162.284 | 164.686 | 164.686 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010590 | 32768 | 77824 |
| metadata after fork samples | 5059270 | 32768 | 77824 |
| metadata before divergence | 5066589 | 962560 | 2007040 |
| metadata after captured divergence | 5473539 | 962560 | 2007040 |
| metadata after divergent snapshots | 5528739 | 999424 | 2084864 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 491520 | 311296 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.489 | 508.732 | 516.638 | 516.638 |
| divergence_bulk_and_capture_ms | 1 | 46.301 | 46.301 | 46.301 | 46.301 |
| divergence_snapshot_ms | 1 | 68.927 | 68.927 | 68.927 | 68.927 |
| explicit_snapshot_ms | 1 | 35.114 | 35.114 | 35.114 | 35.114 |
| first_native_query_ms | 20 | 1.714 | 2.831 | 2.937 | 2.937 |
| head_materialize_after_snapshot_ms | 20 | 17.711 | 19.651 | 20.290 | 20.290 |
| head_materialize_as_shipped_ms | 20 | 17.310 | 18.996 | 37.925 | 37.925 |
| historical_25pct_ms | 20 | 13.561 | 16.500 | 18.245 | 18.245 |
| historical_50pct_ms | 20 | 25.889 | 27.205 | 27.292 | 27.292 |
| import_ms | 1 | 315.822 | 315.822 | 315.822 | 315.822 |
| metadata_fork_ms | 100 | 3.731 | 4.992 | 8.145 | 12.620 |
| native_write_ack_ms | 20 | 1.178 | 2.115 | 2.236 | 2.236 |
| native_write_to_observed_ms | 20 | 507.663 | 510.284 | 518.293 | 518.293 |
| sandbox_capture_ready_ms | 20 | 153.263 | 163.404 | 166.634 | 166.634 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012045 | 32768 | 77824 |
| metadata after fork samples | 5060725 | 815104 | 1871872 |
| metadata before divergence | 5068044 | 1011712 | 2084864 |
| metadata after captured divergence | 5474994 | 1011712 | 2084864 |
| metadata after divergent snapshots | 5530194 | 1011712 | 2084864 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 491520 | 311296 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.387 | 508.720 | 510.360 | 510.360 |
| divergence_bulk_and_capture_ms | 4 | 62.751 | 63.466 | 63.466 | 63.466 |
| divergence_snapshot_ms | 4 | 40.451 | 44.863 | 44.863 | 44.863 |
| explicit_snapshot_ms | 1 | 36.119 | 36.119 | 36.119 | 36.119 |
| first_native_query_ms | 20 | 1.917 | 2.289 | 3.774 | 3.774 |
| head_materialize_after_snapshot_ms | 20 | 20.291 | 23.727 | 25.792 | 25.792 |
| head_materialize_as_shipped_ms | 20 | 20.837 | 25.559 | 25.872 | 25.872 |
| historical_25pct_ms | 20 | 22.220 | 25.056 | 25.069 | 25.069 |
| historical_50pct_ms | 20 | 39.966 | 49.026 | 49.026 | 49.026 |
| import_ms | 1 | 329.362 | 329.362 | 329.362 | 329.362 |
| metadata_fork_ms | 100 | 4.159 | 6.123 | 7.045 | 7.354 |
| native_write_ack_ms | 20 | 1.595 | 4.107 | 4.263 | 4.263 |
| native_write_to_observed_ms | 20 | 507.720 | 511.820 | 512.538 | 512.538 |
| sandbox_capture_ready_ms | 20 | 210.774 | 315.774 | 425.315 | 425.315 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010590 | 32768 | 77824 |
| metadata after fork samples | 5059270 | 32768 | 77824 |
| metadata before divergence | 5069527 | 958464 | 2007040 |
| metadata after captured divergence | 6697329 | 1032192 | 2093056 |
| metadata after divergent snapshots | 6809743 | 1032192 | 2093056 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 495616 | 311296 |
| divergent physical copy 1 | 2343890 | 479232 | 315392 |
| divergent physical copy 2 | 2343890 | 503808 | 311296 |
| divergent physical copy 3 | 2343890 | 491520 | 311296 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.478 | 508.744 | 508.768 | 508.768 |
| divergence_bulk_and_capture_ms | 4 | 65.367 | 65.976 | 65.976 | 65.976 |
| divergence_snapshot_ms | 4 | 40.124 | 43.978 | 43.978 | 43.978 |
| explicit_snapshot_ms | 1 | 39.591 | 39.591 | 39.591 | 39.591 |
| first_native_query_ms | 20 | 2.093 | 2.552 | 4.103 | 4.103 |
| head_materialize_after_snapshot_ms | 20 | 23.872 | 26.755 | 27.573 | 27.573 |
| head_materialize_as_shipped_ms | 20 | 22.614 | 29.489 | 29.507 | 29.507 |
| historical_25pct_ms | 20 | 25.607 | 27.577 | 28.035 | 28.035 |
| historical_50pct_ms | 20 | 44.956 | 50.346 | 50.690 | 50.690 |
| import_ms | 1 | 289.948 | 289.948 | 289.948 | 289.948 |
| metadata_fork_ms | 100 | 3.999 | 5.937 | 7.684 | 7.701 |
| native_write_ack_ms | 20 | 1.503 | 5.046 | 6.086 | 6.086 |
| native_write_to_observed_ms | 20 | 507.176 | 511.456 | 512.375 | 512.375 |
| sandbox_capture_ready_ms | 20 | 212.071 | 322.522 | 432.317 | 432.317 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012045 | 32768 | 77824 |
| metadata after fork samples | 5060725 | 32768 | 77824 |
| metadata before divergence | 5070984 | 966656 | 2007040 |
| metadata after captured divergence | 6698784 | 1032192 | 2023424 |
| metadata after divergent snapshots | 6811380 | 1032192 | 2023424 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 491520 | 311296 |
| divergent physical copy 1 | 2343890 | 495616 | 311296 |
| divergent physical copy 2 | 2343890 | 491520 | 311296 |
| divergent physical copy 3 | 2343890 | 495616 | 311296 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 1 workers · ancestry depth 1

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.842 | 510.700 | 516.611 | 516.611 |
| divergence_bulk_and_capture_ms | 1 | 42.103 | 42.103 | 42.103 | 42.103 |
| divergence_snapshot_ms | 1 | 122.022 | 122.022 | 122.022 | 122.022 |
| explicit_snapshot_ms | 1 | 105.603 | 105.603 | 105.603 | 105.603 |
| first_native_query_ms | 20 | 1.845 | 2.131 | 2.438 | 2.438 |
| head_materialize_after_snapshot_ms | 20 | 34.678 | 36.927 | 37.731 | 37.731 |
| head_materialize_as_shipped_ms | 20 | 34.405 | 39.350 | 52.196 | 52.196 |
| historical_25pct_ms | 20 | 56.538 | 60.828 | 61.687 | 61.687 |
| historical_50pct_ms | 20 | 112.882 | 121.639 | 123.770 | 123.770 |
| import_ms | 1 | 1421.815 | 1421.815 | 1421.815 | 1421.815 |
| metadata_fork_ms | 100 | 3.585 | 4.933 | 5.383 | 5.642 |
| native_write_ack_ms | 20 | 1.099 | 1.836 | 1.924 | 1.924 |
| native_write_to_observed_ms | 20 | 506.662 | 511.391 | 517.612 | 517.612 |
| sandbox_capture_ready_ms | 20 | 498.217 | 553.422 | 584.718 | 584.718 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25075495 | 3362816 | 7942144 |
| metadata after fork samples | 25124175 | 3362816 | 7942144 |
| metadata before divergence | 25131710 | 3997696 | 8863744 |
| metadata after captured divergence | 25538660 | 3997696 | 8863744 |
| metadata after divergent snapshots | 25630495 | 3997696 | 8863744 |
| one observed checkout (first completed) | 11763890 | 1564672 | 1089536 |
| divergent physical copy 0 | 11763890 | 847872 | 552960 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 1 workers · ancestry depth 4

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.435 | 510.444 | 542.377 | 542.377 |
| divergence_bulk_and_capture_ms | 1 | 39.288 | 39.288 | 39.288 | 39.288 |
| divergence_snapshot_ms | 1 | 122.585 | 122.585 | 122.585 | 122.585 |
| explicit_snapshot_ms | 1 | 103.428 | 103.428 | 103.428 | 103.428 |
| first_native_query_ms | 20 | 1.768 | 2.043 | 2.164 | 2.164 |
| head_materialize_after_snapshot_ms | 20 | 34.586 | 36.766 | 37.942 | 37.942 |
| head_materialize_as_shipped_ms | 20 | 34.677 | 37.702 | 40.967 | 40.967 |
| historical_25pct_ms | 20 | 55.992 | 59.129 | 63.076 | 63.076 |
| historical_50pct_ms | 20 | 109.823 | 117.502 | 124.850 | 124.850 |
| import_ms | 1 | 1382.752 | 1382.752 | 1382.752 | 1382.752 |
| metadata_fork_ms | 100 | 2.463 | 4.304 | 4.984 | 5.916 |
| native_write_ack_ms | 20 | 1.170 | 1.596 | 2.288 | 2.288 |
| native_write_to_observed_ms | 20 | 507.407 | 511.979 | 543.203 | 543.203 |
| sandbox_capture_ready_ms | 20 | 515.138 | 565.466 | 565.514 | 565.514 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25076950 | 3584000 | 7266304 |
| metadata after fork samples | 25125630 | 3584000 | 7266304 |
| metadata before divergence | 25133165 | 4128768 | 9121792 |
| metadata after captured divergence | 25540115 | 4128768 | 9121792 |
| metadata after divergent snapshots | 25631950 | 4128768 | 9146368 |
| one observed checkout (first completed) | 11763890 | 1183744 | 1069056 |
| divergent physical copy 0 | 11763890 | 765952 | 499712 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 4 workers · ancestry depth 1

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.873 | 510.871 | 510.965 | 510.965 |
| divergence_bulk_and_capture_ms | 4 | 79.909 | 92.418 | 92.418 | 92.418 |
| divergence_snapshot_ms | 4 | 107.510 | 173.155 | 173.155 | 173.155 |
| explicit_snapshot_ms | 1 | 113.915 | 113.915 | 113.915 | 113.915 |
| first_native_query_ms | 20 | 2.341 | 4.807 | 5.018 | 5.018 |
| head_materialize_after_snapshot_ms | 20 | 75.024 | 92.285 | 96.243 | 96.243 |
| head_materialize_as_shipped_ms | 20 | 77.715 | 83.089 | 86.950 | 86.950 |
| historical_25pct_ms | 20 | 110.828 | 120.074 | 120.614 | 120.614 |
| historical_50pct_ms | 20 | 229.941 | 242.556 | 245.913 | 245.913 |
| import_ms | 1 | 1423.915 | 1423.915 | 1423.915 | 1423.915 |
| metadata_fork_ms | 100 | 3.810 | 5.678 | 6.002 | 6.251 |
| native_write_ack_ms | 20 | 1.761 | 2.024 | 2.025 | 2.025 |
| native_write_to_observed_ms | 20 | 508.493 | 512.369 | 512.687 | 512.687 |
| sandbox_capture_ready_ms | 20 | 1259.142 | 1535.339 | 1797.234 | 1797.234 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25075495 | 3665920 | 8704000 |
| metadata after fork samples | 25124175 | 3665920 | 8704000 |
| metadata before divergence | 25134650 | 4005888 | 8822784 |
| metadata after captured divergence | 26762634 | 4005888 | 8822784 |
| metadata after divergent snapshots | 26949430 | 4005888 | 9170944 |
| one observed checkout (first completed) | 11763890 | 1183744 | 503808 |
| divergent physical copy 0 | 11763890 | 2293760 | 1609728 |
| divergent physical copy 1 | 11763890 | 2240512 | 1703936 |
| divergent physical copy 2 | 11763890 | 2281472 | 1523712 |
| divergent physical copy 3 | 11763890 | 2252800 | 1646592 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 4 workers · ancestry depth 4

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.465 | 508.838 | 508.858 | 508.858 |
| divergence_bulk_and_capture_ms | 4 | 105.663 | 115.674 | 115.674 | 115.674 |
| divergence_snapshot_ms | 4 | 107.044 | 151.056 | 151.056 | 151.056 |
| explicit_snapshot_ms | 1 | 110.722 | 110.722 | 110.722 | 110.722 |
| first_native_query_ms | 20 | 2.278 | 2.793 | 2.798 | 2.798 |
| head_materialize_after_snapshot_ms | 20 | 71.695 | 89.015 | 92.710 | 92.710 |
| head_materialize_as_shipped_ms | 20 | 77.031 | 99.855 | 108.216 | 108.216 |
| historical_25pct_ms | 20 | 112.502 | 130.957 | 132.132 | 132.132 |
| historical_50pct_ms | 20 | 238.594 | 260.436 | 266.886 | 266.886 |
| import_ms | 1 | 1345.643 | 1345.643 | 1345.643 | 1345.643 |
| metadata_fork_ms | 100 | 3.619 | 5.678 | 6.491 | 7.223 |
| native_write_ack_ms | 20 | 1.314 | 2.127 | 4.860 | 4.860 |
| native_write_to_observed_ms | 20 | 507.721 | 510.706 | 513.346 | 513.346 |
| sandbox_capture_ready_ms | 20 | 1208.261 | 1367.073 | 1790.143 | 1790.143 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25076950 | 3141632 | 8200192 |
| metadata after fork samples | 25125630 | 3141632 | 8200192 |
| metadata before divergence | 25136105 | 3973120 | 8855552 |
| metadata after captured divergence | 26764089 | 4177920 | 8855552 |
| metadata after divergent snapshots | 26950885 | 4177920 | 9076736 |
| one observed checkout (first completed) | 11763890 | 1298432 | 913408 |
| divergent physical copy 0 | 11763890 | 2273280 | 1708032 |
| divergent physical copy 1 | 11763890 | 2281472 | 1568768 |
| divergent physical copy 2 | 11763890 | 2252800 | 1544192 |
| divergent physical copy 3 | 11763890 | 2273280 | 1560576 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

