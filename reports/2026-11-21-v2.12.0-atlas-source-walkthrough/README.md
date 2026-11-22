# Argon v2.12.0 with a MongoDB Atlas M0 as the source: online import, following, a sandbox, review and write-back, 2026-11-21

A functional walkthrough with a transcript, not a performance benchmark. It runs the published 2.12.0 CLI through the whole path from an Atlas database that is in use to a reviewed change written back to it, and records every command and its output. The few timings in it are single observations.

## What ran

- **Argon 2.12.0**: the executable that `npm install -g argonctl@2.12.0` installs (`bin/argon-bin`, SHA256 `aec1762051bf962ca485fdc6bceaf6901ce9b09073d2055fbc607bcfa230f339`, equal to the `argon-linux-arm64` asset of release [`v2.12.0`](https://github.com/argon-lab/argon/releases/tag/v2.12.0)).
- **The source**: a free MongoDB Atlas M0 cluster, MongoDB 8.0.39, AWS us-east-1, reached over `mongodb+srv://` with TLS. The database user had `readWriteAnyDatabase`, restricted to that cluster. The run creates the database `shop` and drops it at the end.
- **Argon's own MongoDB**: 7.0.45 as a one-member replica set without access control, in a container on a private Docker network with no published ports. It holds Argon's metadata and the sandboxes.
- **The application**: a thread that makes one write to Atlas (40% inserts, 60% updates), then sleeps 50 ms, for the whole run. It is paused only for the comparison that needs the source to stand still.
- `shop.orders` starts with 2,000 documents and `shop.customers` with 200.
- Window `2026-11-21T23:18:48Z` → `23:19:14Z`. `scripts/atlas_source_walkthrough_docker.sh 2.12.0 <output directory> <file with the Atlas URI> 2000`.

Files: [transcript](transcript.txt), [output of `argon source follow`](follow.log), [binary hash](binary-sha256.txt). The script masks the cluster's SRV host, member hosts and replica-set name as `<id>` and fails if the password or the unmasked host appears in any file; nothing else was edited.

The script calls `argon-bin` directly. Through the npm launcher (`bin/argon.js` in 2.12.0) a SIGINT stopped only the launcher and left `argon source follow` running; an earlier run that went through the launcher showed `State: running` after the stop. [argon-lab/argon#208](https://github.com/argon-lab/argon/pull/208) fixes the launcher for the next release.

## What the transcript shows

1. `argon import database --online` imported the database in 0.9 s while the application made 13 writes to Atlas, and reported the cluster time at which the import equals the source.
2. `argon source status` showed `Identity: replica-set name and TLS-verified MongoDB Atlas hosts`: the M0 refuses `replSetGetConfig`, so the project is bound to the cluster by its TLS-verified `mongodb.net` hosts. With the application writing, changes were reported stored 84 to 96 ms after they happened; with it paused, the newest write was stored 0.5 s after it was made.
3. A sandbox forked from `main` held the same documents as Atlas in both collections (2,077 and 200), with identical BSON bytes.
4. An agent changed one order, inserted one and deleted one in a sandbox. `argon merge preview -o json` gave three changes with their images, `"followed_replica_set_id": "atlas-tls:atlas-<id>-shard-0"` and an `approval_digest`.
5. Refused, with Atlas unchanged: write-back without `--approve`; with a digest of zeros; with a connection string to the engine's deployment instead of Atlas (the Atlas identity check); and an ordinary `merge apply` to the followed `main`.
6. `argon merge apply <plan> --write-back --approve <digest>` wrote the three changes in one transaction in 599 ms. Applying the same plan again was refused.
7. A second plan changed two orders. After the review, one of them was edited directly on Atlas. The write-back aborted and wrote nothing; the other order was unchanged. A fresh preview after following caught up showed one change and one conflict.
8. At the end Atlas held 2,125 orders: 2,000 seeded, 125 inserted by the application, one inserted and one deleted by the plan. A new sandbox forked from `main` held the same documents with identical BSON bytes. `argon source follow` stopped with `Stopped; source position saved.`

## Not covered

Dedicated tiers (M10 and up), Flex, least-privilege custom roles (see the Atlas section of the engine's `docs/OPERATIONS.md`), sharded clusters, the engine running on Atlas, `--credential`, conflicts resolved with `--strategy`, large plans, and any load beyond the one application thread.
