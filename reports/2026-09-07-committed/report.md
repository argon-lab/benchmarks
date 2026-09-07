# Argon workflow benchmark

Completed 2026-09-07 08:05:50 UTC; duration 132.9 seconds. This is an explicitly sourced local diagnostic build, not a released-version claim. Raw samples, build hashes, environment and configuration: `raw.json`.

Percentiles use nearest rank. With fewer than 100 samples, p99 is usually the observed maximum; these are descriptive observations, not a stable tail-latency estimate. All samples, including first execution, are retained. Scenarios run sequentially; workers run closed-loop within a phase.

Sandbox readiness includes metadata fork, full physical checkout, and acknowledged capture startup. First native query includes a new client connection/handshake and one verified indexed read, after readiness. Capture lag is measured from majority write acknowledgement until a committed WAL record is observed; polling and query latency are included.

Metadata forks reference inherited history. Checked-out sandboxes materialize full physical copies. dbStats logical data bytes, allocated collection bytes, and allocated index bytes are reported separately. Allocations are quantized and can remain after deletion; before/after differences are observations, not a universal per-branch disk price.

## 1000 documents · 1 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.622 | 516.718 | 570.353 | 570.353 |
| divergence_bulk_and_capture_ms | 1 | 67.578 | 67.578 | 67.578 | 67.578 |
| divergence_snapshot_ms | 1 | 29.832 | 29.832 | 29.832 | 29.832 |
| explicit_snapshot_ms | 1 | 25.898 | 25.898 | 25.898 | 25.898 |
| first_native_query_ms | 20 | 10.052 | 18.093 | 19.111 | 19.111 |
| head_materialize_after_snapshot_ms | 20 | 3.305 | 3.467 | 3.484 | 3.484 |
| head_materialize_as_shipped_ms | 20 | 3.456 | 3.992 | 4.407 | 4.407 |
| historical_25pct_ms | 20 | 1.856 | 2.490 | 2.857 | 2.857 |
| historical_50pct_ms | 20 | 3.054 | 3.415 | 3.804 | 3.804 |
| import_ms | 1 | 167.287 | 167.287 | 167.287 | 167.287 |
| metadata_fork_ms | 100 | 17.938 | 19.962 | 20.096 | 20.942 |
| native_write_ack_ms | 20 | 5.224 | 9.302 | 10.186 | 10.186 |
| native_write_to_observed_ms | 20 | 518.685 | 524.152 | 575.181 | 575.181 |
| sandbox_capture_ready_ms | 20 | 153.375 | 223.650 | 225.535 | 225.535 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505093 | 32768 | 77824 |
| metadata after fork samples | 553773 | 32768 | 77824 |
| metadata before divergence | 561092 | 36864 | 81920 |
| metadata after captured divergence | 805282 | 36864 | 81920 |
| metadata after divergent snapshots | 814494 | 36864 | 81920 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 1 workers · ancestry depth 4

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.418 | 516.758 | 516.798 | 516.798 |
| divergence_bulk_and_capture_ms | 1 | 68.626 | 68.626 | 68.626 | 68.626 |
| divergence_snapshot_ms | 1 | 28.953 | 28.953 | 28.953 | 28.953 |
| explicit_snapshot_ms | 1 | 26.170 | 26.170 | 26.170 | 26.170 |
| first_native_query_ms | 20 | 9.969 | 12.662 | 28.519 | 28.519 |
| head_materialize_after_snapshot_ms | 20 | 3.620 | 3.935 | 4.082 | 4.082 |
| head_materialize_as_shipped_ms | 20 | 3.956 | 6.004 | 6.779 | 6.779 |
| historical_25pct_ms | 20 | 2.462 | 2.716 | 2.774 | 2.774 |
| historical_50pct_ms | 20 | 3.286 | 3.830 | 3.863 | 3.863 |
| import_ms | 1 | 184.830 | 184.830 | 184.830 | 184.830 |
| metadata_fork_ms | 100 | 19.028 | 31.170 | 32.246 | 38.818 |
| native_write_ack_ms | 20 | 5.617 | 6.848 | 10.306 | 10.306 |
| native_write_to_observed_ms | 20 | 517.033 | 522.866 | 527.103 | 527.103 |
| sandbox_capture_ready_ms | 20 | 152.431 | 173.651 | 259.777 | 259.777 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506548 | 32768 | 77824 |
| metadata after fork samples | 555228 | 32768 | 77824 |
| metadata before divergence | 562547 | 258048 | 540672 |
| metadata after captured divergence | 806737 | 258048 | 540672 |
| metadata after divergent snapshots | 815949 | 258048 | 540672 |
| one observed checkout (first completed) | 233390 | 8192 | 8192 |
| divergent physical copy 0 | 233390 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 1000 documents · 4 workers · ancestry depth 1

Imported head LSN 1002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 510.418 | 512.604 | 520.353 | 520.353 |
| divergence_bulk_and_capture_ms | 4 | 85.970 | 94.672 | 94.672 | 94.672 |
| divergence_snapshot_ms | 4 | 20.672 | 51.683 | 51.683 | 51.683 |
| explicit_snapshot_ms | 1 | 23.296 | 23.296 | 23.296 | 23.296 |
| first_native_query_ms | 20 | 10.603 | 15.111 | 16.188 | 16.188 |
| head_materialize_after_snapshot_ms | 20 | 3.872 | 4.346 | 4.422 | 4.422 |
| head_materialize_as_shipped_ms | 20 | 5.061 | 6.844 | 6.885 | 6.885 |
| historical_25pct_ms | 20 | 2.147 | 3.175 | 3.358 | 3.358 |
| historical_50pct_ms | 20 | 3.359 | 4.296 | 5.467 | 5.467 |
| import_ms | 1 | 169.871 | 169.871 | 169.871 | 169.871 |
| metadata_fork_ms | 100 | 24.829 | 28.037 | 29.265 | 31.468 |
| native_write_ack_ms | 20 | 6.477 | 23.659 | 25.600 | 25.600 |
| native_write_to_observed_ms | 20 | 518.333 | 536.017 | 536.075 | 536.075 |
| sandbox_capture_ready_ms | 20 | 216.734 | 356.619 | 406.526 | 406.526 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 505093 | 32768 | 77824 |
| metadata after fork samples | 553773 | 32768 | 77824 |
| metadata before divergence | 564032 | 36864 | 86016 |
| metadata after captured divergence | 1540724 | 36864 | 86016 |
| metadata after divergent snapshots | 1552139 | 36864 | 86016 |
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
| capture_ack_to_observed_ms | 20 | 508.472 | 514.431 | 534.284 | 534.284 |
| divergence_bulk_and_capture_ms | 4 | 89.878 | 90.317 | 90.317 | 90.317 |
| divergence_snapshot_ms | 4 | 26.322 | 46.596 | 46.596 | 46.596 |
| explicit_snapshot_ms | 1 | 24.437 | 24.437 | 24.437 | 24.437 |
| first_native_query_ms | 20 | 10.933 | 18.027 | 54.998 | 54.998 |
| head_materialize_after_snapshot_ms | 20 | 4.173 | 4.583 | 4.590 | 4.590 |
| head_materialize_as_shipped_ms | 20 | 5.498 | 6.790 | 6.817 | 6.817 |
| historical_25pct_ms | 20 | 2.476 | 3.204 | 3.250 | 3.250 |
| historical_50pct_ms | 20 | 3.818 | 4.718 | 4.870 | 4.870 |
| import_ms | 1 | 171.187 | 171.187 | 171.187 | 171.187 |
| metadata_fork_ms | 100 | 22.982 | 26.067 | 31.279 | 31.304 |
| native_write_ack_ms | 20 | 6.581 | 16.502 | 18.001 | 18.001 |
| native_write_to_observed_ms | 20 | 517.214 | 528.285 | 539.889 | 539.889 |
| sandbox_capture_ready_ms | 20 | 210.779 | 362.456 | 431.646 | 431.646 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 506548 | 32768 | 77824 |
| metadata after fork samples | 555228 | 32768 | 77824 |
| metadata before divergence | 565487 | 36864 | 86016 |
| metadata after captured divergence | 1542063 | 36864 | 86016 |
| metadata after divergent snapshots | 1553594 | 36864 | 86016 |
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
| capture_ack_to_observed_ms | 20 | 512.447 | 514.826 | 516.632 | 516.632 |
| divergence_bulk_and_capture_ms | 1 | 75.836 | 75.836 | 75.836 | 75.836 |
| divergence_snapshot_ms | 1 | 70.957 | 70.957 | 70.957 | 70.957 |
| explicit_snapshot_ms | 1 | 63.068 | 63.068 | 63.068 | 63.068 |
| first_native_query_ms | 20 | 7.449 | 10.618 | 12.006 | 12.006 |
| head_materialize_after_snapshot_ms | 20 | 27.428 | 28.638 | 29.018 | 29.018 |
| head_materialize_as_shipped_ms | 20 | 27.945 | 30.485 | 43.509 | 43.509 |
| historical_25pct_ms | 20 | 12.209 | 12.841 | 13.101 | 13.101 |
| historical_50pct_ms | 20 | 23.584 | 24.359 | 24.681 | 24.681 |
| import_ms | 1 | 515.860 | 515.860 | 515.860 | 515.860 |
| metadata_fork_ms | 100 | 16.907 | 19.978 | 21.103 | 21.159 |
| native_write_ack_ms | 20 | 5.422 | 6.297 | 6.646 | 6.646 |
| native_write_to_observed_ms | 20 | 516.915 | 520.258 | 521.203 | 521.203 |
| sandbox_capture_ready_ms | 20 | 290.317 | 299.106 | 304.456 | 304.456 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010581 | 32768 | 77824 |
| metadata after fork samples | 5059261 | 32768 | 77824 |
| metadata before divergence | 5066580 | 856064 | 1949696 |
| metadata after captured divergence | 5310770 | 856064 | 1949696 |
| metadata after divergent snapshots | 5365970 | 856064 | 1949696 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 1 workers · ancestry depth 4

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 512.497 | 514.692 | 516.657 | 516.657 |
| divergence_bulk_and_capture_ms | 1 | 66.744 | 66.744 | 66.744 | 66.744 |
| divergence_snapshot_ms | 1 | 73.214 | 73.214 | 73.214 | 73.214 |
| explicit_snapshot_ms | 1 | 61.740 | 61.740 | 61.740 | 61.740 |
| first_native_query_ms | 20 | 10.580 | 22.941 | 23.993 | 23.993 |
| head_materialize_after_snapshot_ms | 20 | 27.426 | 28.389 | 28.446 | 28.446 |
| head_materialize_as_shipped_ms | 20 | 27.676 | 28.972 | 37.235 | 37.235 |
| historical_25pct_ms | 20 | 12.662 | 13.448 | 20.945 | 20.945 |
| historical_50pct_ms | 20 | 23.531 | 24.263 | 24.812 | 24.812 |
| import_ms | 1 | 506.431 | 506.431 | 506.431 | 506.431 |
| metadata_fork_ms | 100 | 16.150 | 21.049 | 23.103 | 23.872 |
| native_write_ack_ms | 20 | 5.808 | 8.171 | 11.521 | 11.521 |
| native_write_to_observed_ms | 20 | 518.496 | 523.163 | 526.199 | 526.199 |
| sandbox_capture_ready_ms | 20 | 295.691 | 429.136 | 437.895 | 437.895 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012036 | 36864 | 81920 |
| metadata after fork samples | 5060716 | 36864 | 81920 |
| metadata before divergence | 5068035 | 1687552 | 3817472 |
| metadata after captured divergence | 5312225 | 1687552 | 3817472 |
| metadata after divergent snapshots | 5367425 | 1687552 | 3817472 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |

Divergence captured **300** records: **244140 bytes** of stored WAL BSON over **23240 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

## 10000 documents · 4 workers · ancestry depth 1

Imported head LSN 10002; snapshots present immediately after import: 1.

| Operation | n | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|---:|
| capture_ack_to_observed_ms | 20 | 514.400 | 522.253 | 522.331 | 522.331 |
| divergence_bulk_and_capture_ms | 4 | 89.671 | 99.263 | 99.263 | 99.263 |
| divergence_snapshot_ms | 4 | 67.909 | 82.490 | 82.490 | 82.490 |
| explicit_snapshot_ms | 1 | 66.255 | 66.255 | 66.255 | 66.255 |
| first_native_query_ms | 20 | 14.375 | 22.200 | 23.227 | 23.227 |
| head_materialize_after_snapshot_ms | 20 | 30.824 | 33.069 | 33.175 | 33.175 |
| head_materialize_as_shipped_ms | 20 | 32.849 | 45.924 | 46.233 | 46.233 |
| historical_25pct_ms | 20 | 14.424 | 15.627 | 15.776 | 15.776 |
| historical_50pct_ms | 20 | 28.558 | 30.366 | 30.443 | 30.443 |
| import_ms | 1 | 570.390 | 570.390 | 570.390 | 570.390 |
| metadata_fork_ms | 100 | 31.187 | 60.428 | 67.107 | 67.134 |
| native_write_ack_ms | 20 | 8.483 | 13.277 | 18.243 | 18.243 |
| native_write_to_observed_ms | 20 | 523.759 | 531.393 | 535.607 | 535.607 |
| sandbox_capture_ready_ms | 20 | 447.397 | 904.730 | 1150.878 | 1150.878 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5010581 | 36864 | 81920 |
| metadata after fork samples | 5059261 | 36864 | 81920 |
| metadata before divergence | 5069520 | 860160 | 1961984 |
| metadata after captured divergence | 6046096 | 860160 | 1961984 |
| metadata after divergent snapshots | 6103615 | 860160 | 1961984 |
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
| capture_ack_to_observed_ms | 20 | 510.413 | 516.299 | 524.345 | 524.345 |
| divergence_bulk_and_capture_ms | 4 | 81.204 | 87.647 | 87.647 | 87.647 |
| divergence_snapshot_ms | 4 | 63.855 | 104.455 | 104.455 | 104.455 |
| explicit_snapshot_ms | 1 | 67.985 | 67.985 | 67.985 | 67.985 |
| first_native_query_ms | 20 | 10.650 | 16.288 | 21.401 | 21.401 |
| head_materialize_after_snapshot_ms | 20 | 31.179 | 32.819 | 32.957 | 32.957 |
| head_materialize_as_shipped_ms | 20 | 32.412 | 37.805 | 38.065 | 38.065 |
| historical_25pct_ms | 20 | 15.076 | 16.046 | 16.277 | 16.277 |
| historical_50pct_ms | 20 | 29.400 | 30.513 | 31.183 | 31.183 |
| import_ms | 1 | 537.280 | 537.280 | 537.280 | 537.280 |
| metadata_fork_ms | 100 | 28.068 | 33.036 | 34.059 | 34.875 |
| native_write_ack_ms | 20 | 6.131 | 9.883 | 11.421 | 11.421 |
| native_write_to_observed_ms | 20 | 518.070 | 525.594 | 528.573 | 528.573 |
| sandbox_capture_ready_ms | 20 | 371.455 | 753.806 | 977.852 | 977.852 |

| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |
|---|---:|---:|---:|
| metadata before fork samples | 5012036 | 32768 | 77824 |
| metadata after fork samples | 5060716 | 32768 | 77824 |
| metadata before divergence | 5070975 | 847872 | 1908736 |
| metadata after captured divergence | 6047551 | 847872 | 1908736 |
| metadata after divergent snapshots | 6105070 | 847872 | 1908736 |
| one observed checkout (first completed) | 2343890 | 8192 | 8192 |
| divergent physical copy 0 | 2343890 | 8192 | 8192 |
| divergent physical copy 1 | 2343890 | 8192 | 8192 |
| divergent physical copy 2 | 2343890 | 8192 | 8192 |
| divergent physical copy 3 | 2343890 | 8192 | 8192 |

Divergence captured **1200** records: **976560 bytes** of stored WAL BSON over **92960 bytes** of changed current-document BSON (**10.505×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.

