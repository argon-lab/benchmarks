# What an Argon 2.11.1 sandbox enforces: a transcript

Not a benchmark. This is a run of the published CLI (`npm install -g argonctl@2.11.1`) against MongoDB 7.0.45 with access control, produced by `scripts/sandbox_safety_walkthrough_docker.sh 2.11.1 <dir>`.

**What it shows:**
- An imported collection's unique, compound and TTL indexes are built in a sandbox. The TTL index is built without its expiry.
- A duplicate key is refused inside the sandbox with E11000.
- A sandbox created with `--credential` gets a MongoDB user that can read and write its own database and is refused on another database, on `main`'s database and on `argon_wal`.
- After `argon sandbox discard`, a connection that was already open fails its next write, and a new connection fails to authenticate.
- A branch drops the unique index and inserts a duplicate:
  - merging it into a checked-out `main` fails with E11000 and changes nothing;
  - with `main` released, the merge applies, and the next sandbox reports that the unique index could not be built while building the others.

**How it was run:**
- MongoDB runs with `--auth --keyFile`, and the CLI connects as a root user.
- Nothing is published on the host's ports.
- Every password in `transcript.txt` is replaced by `•••`; the script refuses to finish if either password appears.
- The CLI's `WAL Monitor: Started/Stopped health monitoring` log lines are left out of the transcript.
- `mongod.log.gz` is the server log for the run.

**Not covered:** Atlas, a separate source deployment, and capture of the sandbox's writes. Capture is not started for the `agent-run` sandbox.
