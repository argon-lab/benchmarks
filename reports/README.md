# Reports

Each folder is one recorded run: a README that says what ran, on which release and environment, what it shows and what it does not cover, plus the raw files it was written from. Newest first. **Benchmarks** are timings; **transcripts** record behaviour and are not benchmarks.

| Date | Release | Kind | Report |
| --- | --- | --- | --- |
| 2026-11-21 | 2.12.0 (npm) | transcript | [MongoDB Atlas M0 as the source: online import, following, a sandbox, review and write-back](2026-11-21-v2.12.0-atlas-source-walkthrough/README.md) |
| 2026-11-21 | 2.11.1 (npm) | transcript | [What a sandbox enforces: indexes, a scoped credential, revocation](2026-11-21-v2.11.1-sandbox-safety/README.md) |
| 2026-11-21 | 2.10.0 vs 2.11.1 (npm) | benchmark | [What building indexes adds to a sandbox](2026-11-21-v2.10.0-v2.11.1-index-cost/README.md) |
| 2026-11-20 | 2.9.0 (npm) | benchmark | [Time from `sandbox create` to the first write](2026-11-20-v2.9.0-sandbox-ready/README.md) |
| 2026-11-19 | 2.8.0 (npm) | transcript | [Online import, following, review and write-back on a source being written](2026-11-19-v2.8.0-live-source-walkthrough/README.md) |
| 2026-11-18 | 2.6.0 vs 2.5.0 (npm) | benchmark | [The first diff after a checkout, alternated](2026-11-18-v2.6.0-cli-scale/README.md) |
| 2026-11-18 | 2.5.0, 2.4.0 (npm) | benchmark | [CLI workflow at 10k, 100k and 1m documents](2026-11-18-v2.5.0-cli-scale/README.md) |
| 2026-11-18 | 2.4.0 (npm) | benchmark | [CLI workflow at 10k, 100k and 1m documents](2026-11-18-v2.4.0-cli-scale/README.md) |
| 2026-11-11 | 2.2.0 source | benchmark | [12-cell matrix, containerized MongoDB, with a 2.1.5 baseline](2026-11-11-v2.2.0/README.md) |
| 2026-09-24 | 2.1.2 source | benchmark | [Release matrix: 1k/10k/50k documents, 1/4 workers, 1/4 ancestry levels](2026-09-24-v2.1.2/README.md) |
| 2026-09-07 | committed hardening engine | benchmark | [Committed-engine workflow matrix](2026-09-07-committed/README.md) |
| 2026-09-07 | unpublished source | diagnostic | [Local hardening diagnostic record](2026-09-07-local/README.md) |

Numbers are scoped to their own release, host and load, which each README states; compare only within one report. [RESULTS.md](../RESULTS.md) summarises the headline numbers.

## Adding a report

Create `reports/<UTC date>-v<release>-<topic>/` with a README in the same shape as the others: **What ran** (release and binary hash, MongoDB version and topology, data, the exact command), the files, **What it shows** (each claim traceable to a file), and **Not covered**. Keep raw samples and logs; mask every password and connection-string secret before committing. Add a row above and, for a benchmark, a section at the top of RESULTS.md.
