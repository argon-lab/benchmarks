# Argon v2.8.0: online import, following, a sandbox, review and write-back on a source that keeps being written, 2026-11-19

A functional walkthrough with a transcript, not a performance benchmark. It runs the published 2.8.0 CLI through the whole path from a MongoDB database that is in use to a reviewed change written back to it, and records every command and its output. The few timings in it are single observations on a shared laptop.

## What ran

- **Argon 2.8.0**: the executable that `npm install -g argonctl@2.8.0` installs (`bin/argon-bin`, SHA256 `58ad3b5d4b2bc35fc8086480fddc9e89ec126c2e725fbde2b03926cebd9dbbd7`, equal to the `argon-linux-arm64` asset of release [`v2.8.0`](https://github.com/argon-lab/argon/releases/tag/v2.8.0)).
- **Two MongoDB 7.0.45 deployments**, each a one-member replica set without access control, in containers on a private Docker network with no published ports: `src0` holds the source database `shop`; `rs0` holds Argon's metadata and its sandboxes.
- **The source**: `shop.orders` with 50,000 documents and `shop.customers` with 200. A thread plays the application for the whole run: one write (40% inserts, 60% updates), then 5 ms of sleep. It is paused only for the two comparisons that need the source to stand still, and the transcript says where.
- Window `2026-11-19T13:06:40Z` → `13:07:24Z`. One run. `scripts/live_source_walkthrough_docker.sh 2.8.0 <output directory> 50000`.

Files: [transcript](transcript.txt), [output of `argon source follow`](follow.log), [binary hash](binary-sha256.txt). Nothing in them was edited.

## What the transcript shows

1. `argon import database --online` imported 50,200 documents in 0.9 s while the application made 144 writes to the source, and reported the cluster time at which the import equals the source.
2. `argon source follow` kept `main` current: with the application writing, `argon source status` reported the last change stored 8 ms after it happened; with the application paused, the newest write was stored 12.6 s after it was made (the wait for MongoDB's next idle oplog entry, documented as ten to twenty seconds).
3. A sandbox forked from `main` held the same documents with the same values as the source in both collections (50,608 and 200). **The bytes were not the same: 50,547 of the 50,608 orders had their fields in a different order in the sandbox.**
4. An agent changed one order, inserted one and deleted one in a sandbox. `argon merge preview -o json` gave three changes with their images and an `approval_digest`.
5. Refused, with the source unchanged: write-back without `--approve`; with a digest of zeros; with a connection string to the other deployment; and an ordinary `merge apply` to the followed `main`.
6. `argon merge apply <plan> --write-back --approve <digest>` wrote the three changes in one transaction. Applying the same plan again was refused.
7. **The replaced order came back with its fields in the sandbox's order**, at the top level and inside the `items` array (`_id, status, customer, total_cents, items, placed_at, touches` before; `_id, touches, customer, items, placed_at, status, total_cents, refund_cents` after).
8. A second plan changed two orders. After the review, one of them was edited directly on the source. The write-back aborted and wrote nothing; the other order was unchanged. A fresh preview after following caught up showed one change and one conflict.
9. At the end the source held 51,060 orders: 50,000 seeded, 1,060 inserted by the application, one inserted and one deleted by the plan. The application made 2,498 writes in all. A new sandbox forked from `main` again held the same values as the source.

## Not covered

Atlas, deployments with access control, more than one replica-set member, elections, sharded sources, MongoDB versions other than 7.0, a source and metadata on one deployment, `--auto-resync`, `--enable-source-images`, `argon source resync`, conflicts resolved with `--strategy`, large plans, and any load beyond the one application thread.
