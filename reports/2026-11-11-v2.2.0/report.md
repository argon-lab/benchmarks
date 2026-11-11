# Argon workflow benchmark

Completed 2026-11-11 11:13:18 UTC; duration 185.7 seconds. Measured engine source tag `v2.2.0`, commit `48bd05a262d404277edefb0855ea3043d3563644`. These local measurements are not production latency guarantees. Raw samples, build hashes, environment and configuration: `raw.json`.

Percentiles use nearest rank. With fewer than 100 samples, p99 is usually the observed maximum; these are descriptive observations, not a stable tail-latency estimate. All samples, including first execution, are retained. Scenarios run sequentially; workers run closed-loop within a phase.

Sandbox readiness includes metadata fork, full physical checkout, and acknowledged capture startup. First native query includes a new client connection/handshake and one verified indexed read, after readiness. Capture lag is measured from majority write acknowledgement until a committed WAL record is observed; polling and query latency are included.

Metadata forks reference inherited history. Checked-out sandboxes materialize full physical copies. dbStats logical data bytes, allocated collection bytes, and allocated index bytes are reported separately. Allocations are quantized and can remain after deletion; before/after differences are observations, not a universal per-branch disk price.

## 1000 documents · 1 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.353 | 610.962 | 652.512 | 652.512 |
| divergence_bulk_and_capture_ms | 1 | 43.628 | 43.628 | 43.628 | 43.628 |
| divergence_snapshot_ms | 1 | 21.494 | 21.494 | 21.494 | 21.494 |
| explicit_snapshot_ms | 1 | 8.606 | 8.606 | 8.606 | 8.606 |
| first_native_query_ms | 20 | 1.832 | 2.750 | 2.863 | 2.863 |
| head_materialize_after_snapshot_ms | 20 | 2.070 | 2.415 | 2.427 | 2.427 |
| head_materialize_as_shipped_ms | 20 | 2.679 | 7.180 | 8.616 | 8.616 |
| historical_25pct_ms | 20 | 2.117 | 2.946 | 3.381 | 3.381 |
| historical_50pct_ms | 20 | 2.939 | 3.842 | 3.918 | 3.918 |
| import_ms | 1 | 59.808 | 59.808 | 59.808 | 59.808 |
| metadata_fork_ms | 100 | 1.528 | 2.866 | 4.051 | 4.303 |
| native_write_ack_ms | 20 | 0.613 | 1.739 | 2.040 | 2.040 |
| native_write_to_observed_ms | 20 | 506.814 | 612.701 | 654.035 | 654.035 |
| sandbox_capture_ready_ms | 20 | 40.202 | 46.691 | 50.411 | 50.411 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505124 | 32768 | 77824 |
| metadata after fork samples | 553804 | 32768 | 77824 |
| metadata before divergence | 561145 | 163840 | 323584 |
| metadata after captured divergence | 968095 | 163840 | 323584 |
| metadata after divergent snapshots | 977329 | 163840 | 323584 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 1 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.530 | 506.584 | 506.909 | 506.909 |
| divergence_bulk_and_capture_ms | 1 | 37.437 | 37.437 | 37.437 | 37.437 |
| divergence_snapshot_ms | 1 | 17.495 | 17.495 | 17.495 | 17.495 |
| explicit_snapshot_ms | 1 | 9.992 | 9.992 | 9.992 | 9.992 |
| first_native_query_ms | 20 | 1.846 | 2.206 | 2.512 | 2.512 |
| head_materialize_after_snapshot_ms | 20 | 2.820 | 3.313 | 3.316 | 3.316 |
| head_materialize_as_shipped_ms | 20 | 3.208 | 6.967 | 9.942 | 9.942 |
| historical_25pct_ms | 20 | 2.702 | 3.031 | 4.241 | 4.241 |
| historical_50pct_ms | 20 | 3.608 | 4.720 | 4.919 | 4.919 |
| import_ms | 1 | 68.311 | 68.311 | 68.311 | 68.311 |
| metadata_fork_ms | 100 | 1.992 | 3.978 | 4.500 | 4.776 |
| native_write_ack_ms | 20 | 0.686 | 1.847 | 2.299 | 2.299 |
| native_write_to_observed_ms | 20 | 505.913 | 507.360 | 507.473 | 507.473 |
| sandbox_capture_ready_ms | 20 | 41.659 | 47.169 | 50.310 | 50.310 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506579 | 32768 | 77824 |
| metadata after fork samples | 555259 | 32768 | 77824 |
| metadata before divergence | 562600 | 356352 | 716800 |
| metadata after captured divergence | 969550 | 356352 | 716800 |
| metadata after divergent snapshots | 978784 | 356352 | 716800 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.496 | 508.396 | 508.478 | 508.478 |
| divergence_bulk_and_capture_ms | 4 | 57.132 | 58.157 | 58.157 | 58.157 |
| divergence_snapshot_ms | 4 | 13.814 | 15.407 | 15.407 | 15.407 |
| explicit_snapshot_ms | 1 | 9.738 | 9.738 | 9.738 | 9.738 |
| first_native_query_ms | 20 | 2.014 | 2.690 | 2.757 | 2.757 |
| head_materialize_after_snapshot_ms | 20 | 2.664 | 2.901 | 2.939 | 2.939 |
| head_materialize_as_shipped_ms | 20 | 2.820 | 3.574 | 3.631 | 3.631 |
| historical_25pct_ms | 20 | 3.506 | 4.863 | 5.344 | 5.344 |
| historical_50pct_ms | 20 | 5.429 | 6.954 | 7.743 | 7.743 |
| import_ms | 1 | 60.350 | 60.350 | 60.350 | 60.350 |
| metadata_fork_ms | 100 | 3.735 | 5.366 | 6.089 | 6.174 |
| native_write_ack_ms | 20 | 1.177 | 3.773 | 5.084 | 5.084 |
| native_write_to_observed_ms | 20 | 506.105 | 509.405 | 509.687 | 509.687 |
| sandbox_capture_ready_ms | 20 | 51.107 | 92.750 | 109.628 | 109.628 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505124 | 32768 | 77824 |
| metadata after fork samples | 553804 | 32768 | 77824 |
| metadata before divergence | 564085 | 163840 | 327680 |
| metadata after captured divergence | 2191701 | 163840 | 327680 |
| metadata after divergent snapshots | 2212499 | 163840 | 327680 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |
| divergent physical copy 1 | 233390 | 8192 | 8192 |
| divergent physical copy 2 | 233390 | 61440 | 40960 |
| divergent physical copy 3 | 233390 | 61440 | 40960 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.449 | 508.322 | 510.692 | 510.692 |
| divergence_bulk_and_capture_ms | 4 | 53.579 | 54.359 | 54.359 | 54.359 |
| divergence_snapshot_ms | 4 | 15.945 | 19.680 | 19.680 | 19.680 |
| explicit_snapshot_ms | 1 | 12.848 | 12.848 | 12.848 | 12.848 |
| first_native_query_ms | 20 | 1.803 | 2.659 | 3.018 | 3.018 |
| head_materialize_after_snapshot_ms | 20 | 3.803 | 4.023 | 4.389 | 4.389 |
| head_materialize_as_shipped_ms | 20 | 3.748 | 4.354 | 4.504 | 4.504 |
| historical_25pct_ms | 20 | 5.246 | 8.907 | 9.012 | 9.012 |
| historical_50pct_ms | 20 | 6.117 | 8.108 | 8.193 | 8.193 |
| import_ms | 1 | 52.561 | 52.561 | 52.561 | 52.561 |
| metadata_fork_ms | 100 | 3.816 | 5.240 | 5.921 | 5.999 |
| native_write_ack_ms | 20 | 1.188 | 1.989 | 2.247 | 2.247 |
| native_write_to_observed_ms | 20 | 505.789 | 509.200 | 511.373 | 511.373 |
| sandbox_capture_ready_ms | 20 | 48.498 | 93.889 | 112.770 | 112.770 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506579 | 32768 | 77824 |
| metadata after fork samples | 555259 | 32768 | 77824 |
| metadata before divergence | 565356 | 180224 | 397312 |
| metadata after captured divergence | 2193340 | 180224 | 397312 |
| metadata after divergent snapshots | 2213954 | 180224 | 397312 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |
| divergent physical copy 1 | 233390 | 8192 | 8192 |
| divergent physical copy 2 | 233390 | 8192 | 8192 |
| divergent physical copy 3 | 233390 | 8192 | 8192 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.512 | 524.516 | 560.517 | 560.517 |
| divergence_bulk_and_capture_ms | 1 | 39.759 | 39.759 | 39.759 | 39.759 |
| divergence_snapshot_ms | 1 | 60.927 | 60.927 | 60.927 | 60.927 |
| explicit_snapshot_ms | 1 | 30.917 | 30.917 | 30.917 | 30.917 |
| first_native_query_ms | 20 | 1.805 | 2.112 | 2.282 | 2.282 |
| head_materialize_after_snapshot_ms | 20 | 14.987 | 16.163 | 16.735 | 16.735 |
| head_materialize_as_shipped_ms | 20 | 15.113 | 16.265 | 16.927 | 16.927 |
| historical_25pct_ms | 20 | 12.220 | 13.435 | 14.084 | 14.084 |
| historical_50pct_ms | 20 | 22.352 | 24.485 | 26.799 | 26.799 |
| import_ms | 1 | 226.657 | 226.657 | 226.657 | 226.657 |
| metadata_fork_ms | 100 | 2.329 | 4.122 | 5.912 | 7.271 |
| native_write_ack_ms | 20 | 0.960 | 1.744 | 1.888 | 1.888 |
| native_write_to_observed_ms | 20 | 505.541 | 525.201 | 561.516 | 561.516 |
| sandbox_capture_ready_ms | 20 | 118.585 | 149.831 | 154.191 | 154.191 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010612 | 32768 | 77824 |
| metadata after fork samples | 5059292 | 118784 | 1757184 |
| metadata before divergence | 5066633 | 954368 | 1937408 |
| metadata after captured divergence | 5473583 | 954368 | 1937408 |
| metadata after divergent snapshots | 5528987 | 954368 | 1937408 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.739 | 508.424 | 510.325 | 510.325 |
| divergence_bulk_and_capture_ms | 1 | 37.013 | 37.013 | 37.013 | 37.013 |
| divergence_snapshot_ms | 1 | 50.227 | 50.227 | 50.227 | 50.227 |
| explicit_snapshot_ms | 1 | 31.707 | 31.707 | 31.707 | 31.707 |
| first_native_query_ms | 20 | 1.739 | 2.772 | 3.472 | 3.472 |
| head_materialize_after_snapshot_ms | 20 | 15.884 | 18.625 | 19.174 | 19.174 |
| head_materialize_as_shipped_ms | 20 | 17.650 | 20.497 | 38.473 | 38.473 |
| historical_25pct_ms | 20 | 13.470 | 14.725 | 14.769 | 14.769 |
| historical_50pct_ms | 20 | 24.068 | 26.782 | 26.813 | 26.813 |
| import_ms | 1 | 310.130 | 310.130 | 310.130 | 310.130 |
| metadata_fork_ms | 100 | 3.462 | 4.619 | 4.960 | 5.227 |
| native_write_ack_ms | 20 | 1.106 | 1.949 | 5.186 | 5.186 |
| native_write_to_observed_ms | 20 | 506.634 | 509.510 | 510.894 | 510.894 |
| sandbox_capture_ready_ms | 20 | 138.211 | 155.101 | 161.819 | 161.819 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012067 | 45056 | 241664 |
| metadata after fork samples | 5060747 | 45056 | 241664 |
| metadata before divergence | 5068088 | 946176 | 1912832 |
| metadata after captured divergence | 5475038 | 946176 | 1912832 |
| metadata after divergent snapshots | 5530260 | 946176 | 1912832 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.397 | 508.383 | 516.556 | 516.556 |
| divergence_bulk_and_capture_ms | 4 | 56.245 | 57.682 | 57.682 | 57.682 |
| divergence_snapshot_ms | 4 | 39.391 | 120.878 | 120.878 | 120.878 |
| explicit_snapshot_ms | 1 | 95.824 | 95.824 | 95.824 | 95.824 |
| first_native_query_ms | 20 | 1.892 | 2.094 | 2.823 | 2.823 |
| head_materialize_after_snapshot_ms | 20 | 20.109 | 24.543 | 25.183 | 25.183 |
| head_materialize_as_shipped_ms | 20 | 22.960 | 28.156 | 28.523 | 28.523 |
| historical_25pct_ms | 20 | 22.133 | 28.115 | 28.812 | 28.812 |
| historical_50pct_ms | 20 | 44.408 | 49.824 | 50.566 | 50.566 |
| import_ms | 1 | 313.667 | 313.667 | 313.667 | 313.667 |
| metadata_fork_ms | 100 | 3.883 | 5.379 | 6.039 | 6.292 |
| native_write_ack_ms | 20 | 1.366 | 3.392 | 3.971 | 3.971 |
| native_write_to_observed_ms | 20 | 506.214 | 509.711 | 518.288 | 518.288 |
| sandbox_capture_ready_ms | 20 | 196.311 | 304.244 | 393.171 | 393.171 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010612 | 32768 | 77824 |
| metadata after fork samples | 5059292 | 32768 | 77824 |
| metadata before divergence | 5069573 | 892928 | 1892352 |
| metadata after captured divergence | 6697189 | 892928 | 1892352 |
| metadata after divergent snapshots | 6809963 | 892928 | 2236416 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 454656 | 303104 |
| divergent physical copy 1 | 2343890 | 454656 | 303104 |
| divergent physical copy 2 | 2343890 | 454656 | 303104 |
| divergent physical copy 3 | 2343890 | 483328 | 307200 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.511 | 508.575 | 511.557 | 511.557 |
| divergence_bulk_and_capture_ms | 4 | 56.908 | 59.599 | 59.599 | 59.599 |
| divergence_snapshot_ms | 4 | 40.026 | 46.035 | 46.035 | 46.035 |
| explicit_snapshot_ms | 1 | 33.371 | 33.371 | 33.371 | 33.371 |
| first_native_query_ms | 20 | 1.952 | 3.863 | 4.530 | 4.530 |
| head_materialize_after_snapshot_ms | 20 | 20.592 | 23.708 | 24.777 | 24.777 |
| head_materialize_as_shipped_ms | 20 | 21.170 | 24.787 | 24.934 | 24.934 |
| historical_25pct_ms | 20 | 23.408 | 30.172 | 30.256 | 30.256 |
| historical_50pct_ms | 20 | 47.445 | 55.925 | 57.555 | 57.555 |
| import_ms | 1 | 324.465 | 324.465 | 324.465 | 324.465 |
| metadata_fork_ms | 100 | 3.694 | 4.969 | 5.713 | 5.849 |
| native_write_ack_ms | 20 | 1.428 | 5.107 | 6.636 | 6.636 |
| native_write_to_observed_ms | 20 | 507.639 | 510.989 | 513.448 | 513.448 |
| sandbox_capture_ready_ms | 20 | 220.132 | 303.065 | 393.027 | 393.027 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012067 | 307200 | 663552 |
| metadata after fork samples | 5060747 | 307200 | 663552 |
| metadata before divergence | 5071026 | 1015808 | 2203648 |
| metadata after captured divergence | 6698644 | 1015808 | 2203648 |
| metadata after divergent snapshots | 6811418 | 1015808 | 2318336 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 454656 | 303104 |
| divergent physical copy 1 | 2343890 | 454656 | 303104 |
| divergent physical copy 2 | 2343890 | 405504 | 270336 |
| divergent physical copy 3 | 2343890 | 491520 | 303104 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 1 workers · ancestry depth 1

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 504.773 | 508.597 | 512.490 | 512.490 |
| divergence_bulk_and_capture_ms | 1 | 49.858 | 49.858 | 49.858 | 49.858 |
| divergence_snapshot_ms | 1 | 121.818 | 121.818 | 121.818 | 121.818 |
| explicit_snapshot_ms | 1 | 105.107 | 105.107 | 105.107 | 105.107 |
| first_native_query_ms | 20 | 1.767 | 2.410 | 4.172 | 4.172 |
| head_materialize_after_snapshot_ms | 20 | 32.937 | 36.980 | 38.259 | 38.259 |
| head_materialize_as_shipped_ms | 20 | 33.947 | 35.632 | 50.943 | 50.943 |
| historical_25pct_ms | 20 | 55.682 | 59.580 | 64.015 | 64.015 |
| historical_50pct_ms | 20 | 109.586 | 118.075 | 118.741 | 118.741 |
| import_ms | 1 | 1430.226 | 1430.226 | 1430.226 | 1430.226 |
| metadata_fork_ms | 100 | 3.398 | 5.018 | 6.472 | 6.534 |
| native_write_ack_ms | 20 | 0.961 | 1.787 | 1.797 | 1.797 |
| native_write_to_observed_ms | 20 | 506.187 | 510.351 | 514.029 | 514.029 |
| sandbox_capture_ready_ms | 20 | 507.723 | 542.969 | 543.002 | 543.002 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25075517 | 3657728 | 8351744 |
| metadata after fork samples | 25124197 | 3657728 | 8351744 |
| metadata before divergence | 25131754 | 3997696 | 8523776 |
| metadata after captured divergence | 25538704 | 3997696 | 8523776 |
| metadata after divergent snapshots | 25630561 | 3997696 | 8556544 |
| one observed checkout (first completed) | 11763890 | 1638400 | 434176 |
| divergent physical copy 0 | 11763890 | 2236416 | 1568768 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 1 workers · ancestry depth 4

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.418 | 508.828 | 522.670 | 522.670 |
| divergence_bulk_and_capture_ms | 1 | 39.258 | 39.258 | 39.258 | 39.258 |
| divergence_snapshot_ms | 1 | 138.088 | 138.088 | 138.088 | 138.088 |
| explicit_snapshot_ms | 1 | 107.255 | 107.255 | 107.255 | 107.255 |
| first_native_query_ms | 20 | 1.795 | 2.290 | 4.006 | 4.006 |
| head_materialize_after_snapshot_ms | 20 | 35.648 | 39.317 | 40.536 | 40.536 |
| head_materialize_as_shipped_ms | 20 | 35.704 | 38.397 | 52.176 | 52.176 |
| historical_25pct_ms | 20 | 59.566 | 64.268 | 65.517 | 65.517 |
| historical_50pct_ms | 20 | 116.239 | 124.191 | 124.812 | 124.812 |
| import_ms | 1 | 1392.620 | 1392.620 | 1392.620 | 1392.620 |
| metadata_fork_ms | 100 | 3.524 | 6.055 | 7.535 | 7.927 |
| native_write_ack_ms | 20 | 1.264 | 2.003 | 2.291 | 2.291 |
| native_write_to_observed_ms | 20 | 507.439 | 510.328 | 523.759 | 523.759 |
| sandbox_capture_ready_ms | 20 | 515.072 | 601.544 | 608.081 | 608.081 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25076972 | 3158016 | 7540736 |
| metadata after fork samples | 25125652 | 3158016 | 7540736 |
| metadata before divergence | 25133209 | 4169728 | 9080832 |
| metadata after captured divergence | 25540159 | 4169728 | 9080832 |
| metadata after divergent snapshots | 25632016 | 4169728 | 9080832 |
| one observed checkout (first completed) | 11763890 | 1183744 | 897024 |
| divergent physical copy 0 | 11763890 | 2248704 | 1130496 |

Divergence captured **500** records: **406900 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 4 workers · ancestry depth 1

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.287 | 508.497 | 509.087 | 509.087 |
| divergence_bulk_and_capture_ms | 4 | 83.843 | 88.068 | 88.068 | 88.068 |
| divergence_snapshot_ms | 4 | 104.280 | 147.252 | 147.252 | 147.252 |
| explicit_snapshot_ms | 1 | 105.156 | 105.156 | 105.156 | 105.156 |
| first_native_query_ms | 20 | 2.127 | 3.159 | 3.644 | 3.644 |
| head_materialize_after_snapshot_ms | 20 | 68.938 | 86.418 | 95.091 | 95.091 |
| head_materialize_as_shipped_ms | 20 | 70.121 | 81.536 | 91.548 | 91.548 |
| historical_25pct_ms | 20 | 118.659 | 130.813 | 130.845 | 130.845 |
| historical_50pct_ms | 20 | 209.103 | 256.436 | 256.467 | 256.467 |
| import_ms | 1 | 1485.892 | 1485.892 | 1485.892 | 1485.892 |
| metadata_fork_ms | 100 | 3.923 | 5.778 | 6.176 | 6.388 |
| native_write_ack_ms | 20 | 1.284 | 2.654 | 9.024 | 9.024 |
| native_write_to_observed_ms | 20 | 507.416 | 510.029 | 513.949 | 513.949 |
| sandbox_capture_ready_ms | 20 | 1158.821 | 1357.438 | 1765.293 | 1765.293 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25075517 | 3276800 | 7417856 |
| metadata after fork samples | 25124197 | 3276800 | 7417856 |
| metadata before divergence | 25134694 | 3985408 | 8867840 |
| metadata after captured divergence | 26762310 | 3985408 | 8867840 |
| metadata after divergent snapshots | 26949650 | 3985408 | 9125888 |
| one observed checkout (first completed) | 11763890 | 1609728 | 1093632 |
| divergent physical copy 0 | 11763890 | 2277376 | 1622016 |
| divergent physical copy 1 | 11763890 | 2277376 | 1556480 |
| divergent physical copy 2 | 11763890 | 2273280 | 1597440 |
| divergent physical copy 3 | 11763890 | 2260992 | 1748992 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 50000 documents · 4 workers · ancestry depth 4

Imported head LSN 50002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 506.498 | 508.900 | 509.591 | 509.591 |
| divergence_bulk_and_capture_ms | 4 | 77.869 | 92.271 | 92.271 | 92.271 |
| divergence_snapshot_ms | 4 | 104.005 | 165.338 | 165.338 | 165.338 |
| explicit_snapshot_ms | 1 | 110.501 | 110.501 | 110.501 | 110.501 |
| first_native_query_ms | 20 | 2.141 | 2.676 | 7.601 | 7.601 |
| head_materialize_after_snapshot_ms | 20 | 66.737 | 85.719 | 92.249 | 92.249 |
| head_materialize_as_shipped_ms | 20 | 73.422 | 83.501 | 107.624 | 107.624 |
| historical_25pct_ms | 20 | 108.374 | 122.453 | 122.865 | 122.865 |
| historical_50pct_ms | 20 | 233.537 | 245.422 | 246.811 | 246.811 |
| import_ms | 1 | 1462.630 | 1462.630 | 1462.630 | 1462.630 |
| metadata_fork_ms | 100 | 3.610 | 4.712 | 4.984 | 5.060 |
| native_write_ack_ms | 20 | 1.572 | 2.099 | 2.127 | 2.127 |
| native_write_to_observed_ms | 20 | 507.851 | 511.027 | 511.456 | 511.456 |
| sandbox_capture_ready_ms | 20 | 1277.376 | 1364.070 | 1778.076 | 1778.076 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 25076972 | 3493888 | 8376320 |
| metadata after fork samples | 25125652 | 3493888 | 8376320 |
| metadata before divergence | 25136149 | 3989504 | 8843264 |
| metadata after captured divergence | 26763949 | 3989504 | 8843264 |
| metadata after divergent snapshots | 26951105 | 4427776 | 9158656 |
| one observed checkout (first completed) | 11763890 | 1699840 | 1171456 |
| divergent physical copy 0 | 11763890 | 2273280 | 1650688 |
| divergent physical copy 1 | 11763890 | 2273280 | 1564672 |
| divergent physical copy 2 | 11763890 | 2281472 | 1560576 |
| divergent physical copy 3 | 11763890 | 2273280 | 1581056 |

Divergence captured **2000** records: **1627600 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**17.509×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

