#!/usr/bin/env python3
"""Time what an agent waits for before it can write to a new Argon sandbox.

For each fixture (document count and layout) the suite seeds a quiesced source,
imports it, then repeats one round per sample:

* ready: start `argon sandbox create --watch --output json` and stop the clock
  when its JSON reply is complete. The sandbox is forked, checked out and its
  capture is running at that point. Then connect with the returned connection
  string, insert one document with majority write concern (first write
  acknowledged) and wait until that write is visible in Argon's WAL (captured).
* phases: on a separate fresh branch, time `argon branches create` (fork) and
  `argon checkout` (physical copy, including index builds), and record the size
  of the copy. Capture start-up is not timed on its own; it is what remains of
  the ready time.

A concurrency fixture starts several `sandbox create --watch` processes at the
same moment from the same parent and records each one's ready time and the
wall time until all are ready.

Every timing is the monotonic wall clock around a whole CLI process or driver
call, measured inside the runner container.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time
import uuid

from pymongo import ASCENDING, MongoClient
from pymongo.write_concern import WriteConcern

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cli_scale import Runner, db_size, drop_fixture  # noqa: E402

PAYLOAD = "x" * 900  # about 1 KB of BSON per document with the other fields
READY_TIMEOUT_SECONDS = 3600
CAPTURE_TIMEOUT_SECONDS = 60


def document(i: int) -> dict:
    return {"_id": f"item-{i:08d}", "name": f"Item {i}", "qty": 0, "price": (i % 10000) / 100,
            "category": f"cat-{i % 20}", "sku": f"sku-{i:08d}", "payload": PAYLOAD}


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def summarize(values: list[float]) -> dict:
    return {"n": len(values), "median": median(values), "min": min(values), "max": max(values)}


def collections_for(layout: str) -> list[str]:
    return ["items"] if layout == "one" else [f"items_{c}" for c in range(10)]


def seed(client: MongoClient, source: str, n: int, layout: str) -> None:
    names = collections_for(layout)
    per = n // len(names)
    for c, name in enumerate(names):
        coll = client[source].get_collection(name, write_concern=WriteConcern("majority"))
        if layout == "ten":
            coll.create_index([("category", ASCENDING), ("price", ASCENDING)])
            coll.create_index([("sku", ASCENDING)], unique=True)
        base = c * per
        for start in range(0, per, 1000):
            coll.insert_many([document(base + i) for i in range(start, min(per, start + 1000))])


class Watcher:
    """One `argon sandbox create --watch` process, read until its JSON reply."""

    def __init__(self, run: Runner, project: str, name: str):
        self.started = time.monotonic()
        run.note(f"$ argon sandbox create -p {project} --name {name} --watch --output json")
        self.process = subprocess.Popen([str(run.binary), "sandbox", "create", "-p", project, "--name", name,
                                         "--watch", "--output", "json"], env=run.env,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.reply: dict | None = None
        self.ready_ms: float | None = None
        self.error: str | None = None
        self.stderr: list[str] = []
        self.done = threading.Event()
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._drain, daemon=True).start()

    def _read(self) -> None:
        buffer = ""
        for line in self.process.stdout:
            buffer += line
            try:
                self.reply = json.loads(buffer)
            except json.JSONDecodeError:
                continue
            self.ready_ms = (time.monotonic() - self.started) * 1000
            break
        if self.reply is None:
            self.error = f"exited {self.process.wait()} before a JSON reply"
        self.done.set()
        for _ in self.process.stdout:  # keep the pipe drained while capture runs
            pass

    def _drain(self) -> None:
        for line in self.process.stderr:
            self.stderr.append(line.rstrip("\n"))

    def wait_ready(self) -> dict:
        if not self.done.wait(READY_TIMEOUT_SECONDS):
            self.process.kill()
            raise RuntimeError("sandbox create did not reply in time")
        if self.reply is None:
            raise RuntimeError(f"sandbox create failed: {self.error}: {' | '.join(self.stderr[-5:])}")
        return self.reply

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.send_signal(signal.SIGINT)
            try:
                self.process.wait(60)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()


def first_write(uri: str, collection: str) -> tuple[float, str]:
    """Connect fresh and insert one document; return (ms to acknowledgement, _id)."""
    marker = f"probe-{uuid.uuid4().hex[:12]}"
    started = time.monotonic()
    client = MongoClient(uri, serverSelectionTimeoutMS=20000)
    try:
        client.get_default_database().get_collection(collection, write_concern=WriteConcern("majority")).insert_one(
            {"_id": marker, "qty": 1})
    finally:
        client.close()
    return (time.monotonic() - started) * 1000, marker


def wait_captured(client: MongoClient, meta: str, branch_id: str, collection: str) -> float:
    started = time.monotonic()
    wal = client[meta].wal_log
    while time.monotonic() - started < CAPTURE_TIMEOUT_SECONDS:
        if wal.find_one({"branch_id": branch_id, "collection": collection}, {"_id": 1}):
            return (time.monotonic() - started) * 1000
        time.sleep(0.002)
    raise RuntimeError("the probe write was not captured within the timeout")


def fixture(run: Runner, n: int, layout: str, rounds: int, concurrency: list[int], concurrency_rounds: int) -> dict:
    suffix = uuid.uuid4().hex[:12]
    meta, source, project = f"argonbench_ready_meta_{suffix}", f"argonbench_ready_src_{suffix}", f"ready-{layout}-{n}"
    client = run.client
    run.use(meta)
    run.samples = []
    run.cli_peak_rss_kb = {}
    probe_collection = collections_for(layout)[0]
    result: dict = {"documents": n, "layout": layout, "collections": len(collections_for(layout)), "storage": {}}
    run.note(f"\n===== {n} documents, layout {layout}: metadata {meta}, source {source} =====")
    try:
        started = time.monotonic()
        seed(client, source, n, layout)
        run.add("seed_ms", 0, (time.monotonic() - started) * 1000)
        result["storage"]["source"] = db_size(client, source)
        _, ms = run.cli("import", "import", "database", "--uri", run.uri, "--database", source, "--project", project,
                        "--source-quiesced", "--yes", "--output", "json")
        run.add("import_ms", 0, ms)

        for i in range(rounds):
            w = Watcher(run, project, f"r{i}")
            try:
                reply = w.wait_ready()
                run.add("ready_ms", i, w.ready_ms)
                ack_ms, _ = first_write(reply["connection_string"], probe_collection)
                run.add("first_write_ack_ms", i, ack_ms)
                run.add("create_to_first_write_ms", i, w.ready_ms + ack_ms)
                run.add("ack_to_captured_ms", i, wait_captured(client, meta, reply["branch_id"], probe_collection))
                if "sandbox" not in result["storage"]:
                    result["storage"]["sandbox"] = db_size(client, reply["physical_db"])
            finally:
                w.stop()
                run.note("[stderr] " + "\n[stderr] ".join(w.stderr[-20:]))
            run.cli("sandbox_discard", "sandbox", "discard", "-p", project, "-b", f"r{i}", "--output", "json")

            _, ms = run.cli("fork", "branches", "create", f"p{i}", "-p", project, "--from", "main", "--output", "json")
            run.add("fork_ms", i, ms)
            out, ms = run.cli("checkout", "checkout", "-p", project, "-b", f"p{i}", "--output", "json")
            run.add("checkout_ms", i, ms)
            run.cli("sandbox_discard", "sandbox", "discard", "-p", project, "-b", f"p{i}", "--output", "json")
            print(f"  round {i}: ready {run.samples[-6]['ms']:.0f} ms", flush=True)

        groups = []
        for k in concurrency:
            for r in range(concurrency_rounds):
                started = time.monotonic()
                watchers = [Watcher(run, project, f"c{k}-{r}-{j}") for j in range(k)]
                try:
                    replies = [w.wait_ready() for w in watchers]
                    wall = (time.monotonic() - started) * 1000
                    for j, w in enumerate(watchers):
                        run.add("concurrent_ready_ms", r, w.ready_ms, concurrency=k, member=j)
                    run.add("concurrent_group_wall_ms", r, wall, concurrency=k)
                    for j, reply in enumerate(replies):
                        ack_ms, _ = first_write(reply["connection_string"], probe_collection)
                        run.add("concurrent_first_write_ack_ms", r, ack_ms, concurrency=k, member=j)
                finally:
                    for w in watchers:
                        w.stop()
                for j in range(k):
                    run.cli("sandbox_discard", "sandbox", "discard", "-p", project, "-b", f"c{k}-{r}-{j}", "--output", "json")
                groups.append({"concurrency": k, "round": r, "wall_ms": wall})
                print(f"  concurrency {k} round {r}: all ready in {wall:.0f} ms", flush=True)
    finally:
        drop_fixture(client, meta, source)

    summaries: dict = {}
    for sample in run.samples:
        key = sample["operation"] + (f"@{sample['concurrency']}" if "concurrency" in sample else "")
        summaries.setdefault(key, []).append(sample["ms"])
    result["samples"] = run.samples
    result["summaries"] = {key: summarize(values) for key, values in sorted(summaries.items())}
    result["cli_peak_rss_kb"] = dict(run.cli_peak_rss_kb)
    return result


def markdown(report: dict) -> str:
    env, lines = report["environment"], []
    lines += [f"# Argon {report['version']}: time from `sandbox create` to the first write", "",
              f"Window: `{report['started_at']}` → `{report['finished_at']}`. Complete: **{report['complete']}**.", "",
              f"Binary SHA256 `{report['binary_sha256']}`; MongoDB {env['mongodb_version']}; WiredTiger cache "
              f"{env['wiredtiger_cache_bytes'] / 2**30:.2f} GiB; {env['logical_cpus']} logical CPUs visible.", "",
              "Milliseconds, median (min–max). `ready` ends when `sandbox create --watch` has replied: forked, "
              "checked out, capture running. `fork` and `checkout` are timed separately on another fresh branch.", ""]
    for fx in report["fixtures"]:
        lines += [f"## {fx['documents']:,} documents in {fx['collections']} collection(s)", "",
                  "| Measure | n | median | min | max |", "|---|---:|---:|---:|---:|"]
        for key, s in fx["summaries"].items():
            lines.append(f"| `{key}` | {s['n']} | {s['median']:.0f} | {s['min']:.0f} | {s['max']:.0f} |")
        lines += ["", "| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |",
                  "|---|---:|---:|---:|---:|"]
        for label, s in fx["storage"].items():
            lines.append(f"| {label} | {s['objects']} | {s['logical_data_bytes']} | {s['allocated_storage_bytes']} | {s['allocated_index_bytes']} |")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--fixtures", default="10000:one,100000:one,1000000:one,100000:ten,1000000:ten",
                        help="comma-separated documents:layout (one collection, or ten with two secondary indexes each)")
    parser.add_argument("--rounds", type=int, default=8)
    parser.add_argument("--concurrency", default="1,4,16", help="group sizes, run on the --concurrency-fixture")
    parser.add_argument("--concurrency-fixture", default="100000:one")
    parser.add_argument("--concurrency-rounds", type=int, default=8)
    parser.add_argument("--host-info", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fixtures = [(int(f.split(":")[0]), f.split(":")[1]) for f in args.fixtures.split(",") if f]
    concurrency = [int(k) for k in args.concurrency.split(",") if k]
    cfix = tuple(args.concurrency_fixture.split(":"))
    binary = args.binary.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/?replicaSet=rs0")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    reported = subprocess.run([str(binary), "--version"], capture_output=True, text=True, check=True).stdout.strip()
    if reported.split()[-1] != args.version:
        raise SystemExit(f"binary reports {reported!r}, expected version {args.version}")
    status = client.admin.command("serverStatus")
    environment = {
        "mongodb_version": client.server_info()["version"],
        "wiredtiger_cache_bytes": int(status["wiredTiger"]["cache"]["maximum bytes configured"]),
        "platform": platform.platform(), "machine": platform.machine(), "python": platform.python_version(),
        "logical_cpus": os.cpu_count(),
        "isolation": "shared developer host; background load is sampled in host-load.log, not controlled",
        "host": json.loads(args.host_info.read_text()) if args.host_info else None,
    }
    report = {"schema_version": 1, "kind": "sandbox-ready", "version": args.version, "reported_version": reported,
              "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
              "config": {"fixtures": fixtures, "rounds": args.rounds, "concurrency": concurrency,
                         "concurrency_fixture": cfix, "concurrency_rounds": args.concurrency_rounds,
                         "document": "string _id item-%08d, name, qty, price, category, sku, 900-byte payload"},
              "environment": environment, "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "fixtures": [], "complete": False}
    try:
        with (args.output / "commands.log").open("w") as log:
            run = Runner(binary, uri, log, client)
            for n, layout in fixtures:
                print(f"fixture documents={n} layout={layout}", flush=True)
                groups = concurrency if (str(n), layout) == cfix else []
                report["fixtures"].append(fixture(run, n, layout, args.rounds, groups, args.concurrency_rounds))
                (args.output / "raw.json").write_text(json.dumps(report, indent=2) + "\n")
            report["complete"] = True
    finally:
        report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (args.output / "raw.json").write_text(json.dumps(report, indent=2) + "\n")
        if report["fixtures"]:
            (args.output / "report.md").write_text(markdown(report))
        client.close()
    if not report["complete"]:
        raise SystemExit("run did not complete; inspect raw.json and commands.log")
    print(markdown(report))


if __name__ == "__main__":
    main()
