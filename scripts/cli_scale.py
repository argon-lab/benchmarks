#!/usr/bin/env python3
"""Time the published Argon CLI's branch workflow as the imported database grows.

For each document count this seeds a source database, imports it with the
supplied release CLI, then repeats: create a branch, check it out, read from it,
update documents through the driver while `argon watch` captures them, diff,
preview a merge and apply it. It also times `argon sandbox create` to a first
read and point reads by `_id` on a checked-out branch.

Requires pymongo and a disposable MongoDB 7+ replica set. Every scenario uses
its own metadata, source and branch databases and removes them afterwards. The
normal `argon_wal` metadata database is never used. Timings are wall clock
around whole CLI processes, so they include process start-up and connection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import random
import signal
import subprocess
import tempfile
import threading
import time
import uuid

from pymongo import MongoClient, UpdateOne
from pymongo.write_concern import WriteConcern

PAYLOAD = "x" * 128
CLI_TIMEOUT_SECONDS = 3600
RSS_SAMPLE_SECONDS = 0.02


def document(i: int) -> dict:
    # Same shape as the Go suite's seed() in main.go.
    return {"_id": f"item-{i:08d}", "name": f"Item {i}", "qty": 0, "price": (i % 10000) / 100,
            "category": f"cat-{i % 20}", "payload": PAYLOAD}


def nearest_rank(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    rank = max(1, -(-len(ordered) * pct // 100))
    return ordered[int(rank) - 1]


def summarize(values: list[float]) -> dict:
    return {"n": len(values), "min": min(values), "p50": nearest_rank(values, 50),
            "p95": nearest_rank(values, 95), "max": max(values), "mean": sum(values) / len(values)}


def db_size(client: MongoClient, name: str) -> dict:
    stats = client[name].command("dbStats", scale=1)
    return {"logical_data_bytes": int(stats["dataSize"]), "allocated_storage_bytes": int(stats["storageSize"]),
            "allocated_index_bytes": int(stats["indexSize"]), "objects": int(stats["objects"])}


class Runner:
    def __init__(self, binary: Path, uri: str, log, client: MongoClient):
        self.binary, self.uri, self.log, self.client = binary, uri, log, client
        self.env = None
        self.samples: list[dict] = []
        self.cli_peak_rss_kb: dict[str, int] = {}

    def use(self, meta: str) -> None:
        self.env = dict(os.environ, MONGODB_URI=self.uri, ARGON_METADATA_DB=meta)
        for name in ("ARGON_DEMO_MODE", "ARGON_API_TOKEN", "ARGON_READ_ONLY", "ARGON_SNAPSHOT_STORE"):
            self.env.pop(name, None)

    def note(self, text: str) -> None:
        self.log.write(text + "\n")
        self.log.flush()

    def add(self, operation: str, iteration: int, value: float, unit: str = "ms", **extra) -> None:
        self.samples.append({"operation": operation, "iteration": iteration, unit: value, **extra})

    def cli(self, label: str, *args: str, parse: bool = True):
        """Run one CLI process to completion; return (stdout value, elapsed ms)."""
        self.note(f"$ argon {' '.join(args)}")
        with tempfile.TemporaryFile("w+") as out_file, tempfile.TemporaryFile("w+") as err_file:
            waited: dict = {}
            started = time.monotonic()
            process = subprocess.Popen([str(self.binary), *args], env=self.env, stdout=out_file, stderr=err_file)

            def reap() -> None:
                status = os.waitpid(process.pid, 0)[1]
                waited.update(status=status, elapsed=(time.monotonic() - started) * 1000)

            reaper = threading.Thread(target=reap, daemon=True)
            reaper.start()
            # Linux carries a parent's memory high-water mark across exec, so the
            # child's rusage cannot be used. Sample the kernel's own VmHWM instead.
            peak_kb, status_file = 0, Path(f"/proc/{process.pid}/status")
            while reaper.is_alive():
                try:
                    for line in status_file.read_text().splitlines():
                        if line.startswith("VmHWM:"):
                            peak_kb = max(peak_kb, int(line.split()[1]))
                except (OSError, ValueError):
                    pass
                if time.monotonic() - started > CLI_TIMEOUT_SECONDS:
                    process.kill()
                    reaper.join()
                    raise RuntimeError(f"argon {' '.join(args)} exceeded {CLI_TIMEOUT_SECONDS}s")
                reaper.join(RSS_SAMPLE_SECONDS)
            elapsed = waited["elapsed"]
            process.returncode = os.waitstatus_to_exitcode(waited["status"])
            out_file.seek(0)
            err_file.seek(0)
            out, err = out_file.read(), err_file.read()
        self.cli_peak_rss_kb[label] = max(self.cli_peak_rss_kb.get(label, 0), peak_kb)
        shown = out if len(out) <= 4000 else out[:2000] + f"\n… {len(out) - 4000} characters omitted …\n" + out[-2000:]
        self.note(shown.rstrip("\n"))
        if err.strip():
            self.note("[stderr] " + err.strip().replace("\n", "\n[stderr] "))
        self.note(f"[exit {process.returncode}, {elapsed:.1f} ms, sampled peak RSS {peak_kb} kB]")
        if process.returncode != 0:
            raise RuntimeError(f"argon {' '.join(args)} exited {process.returncode}: {err.strip()[-400:]}")
        return (json.loads(out) if parse else out), elapsed


def first_read(uri: str, known_id: str) -> float:
    started = time.monotonic()
    client = MongoClient(uri, serverSelectionTimeoutMS=20000)
    try:
        found = client.get_default_database().items.find_one({"_id": known_id})
    finally:
        client.close()
    if not found or found["_id"] != known_id:
        raise RuntimeError("first read did not return the known document")
    return (time.monotonic() - started) * 1000


def scenario(run: Runner, n: int, args) -> dict:
    suffix = uuid.uuid4().hex[:12]
    meta, source, project = f"argonbench_cli_meta_{suffix}", f"argonbench_cli_src_{suffix}", f"scale-{n}"
    client = run.client
    run.use(meta)
    run.samples = []
    run.cli_peak_rss_kb = {}
    rng = random.Random(20261117 + n)
    result = {"documents": n, "storage": {}, "counts": {}}
    watchers: list[subprocess.Popen] = []
    run.note(f"\n===== {n} documents: metadata {meta}, source {source}, project {project} =====")
    try:
        majority = client[source].get_collection("items", write_concern=WriteConcern("majority"))
        started = time.monotonic()
        for start in range(0, n, 1000):
            majority.insert_many([document(i) for i in range(start, min(n, start + 1000))])
        run.add("seed_native_insert_ms", 0, (time.monotonic() - started) * 1000)
        result["storage"]["source"] = db_size(client, source)

        # Seed writes are acknowledged and nothing else writes to the source:
        # this is the quiesced source the import contract asks for.
        imported, ms = run.cli("import", "import", "database", "--uri", run.uri, "--database", source,
                               "--project", project, "--source-quiesced", "--yes", "--output", "json")
        run.add("import_ms", 0, ms)
        result["import_result"] = imported
        result["storage"]["metadata_after_import"] = db_size(client, meta)

        main, ms = run.cli("checkout", "checkout", "-p", project, "-b", "main", "--output", "json")
        run.add("main_checkout_ms", 0, ms)
        main_db = main["physical_db"]
        if client[main_db].items.count_documents({}) != n:
            raise RuntimeError("checked-out main does not hold every imported document")
        result["storage"]["main_checkout"] = db_size(client, main_db)

        expected_main: dict[str, int] = {}
        point_reads_done = False
        for changed in args.update_sizes:
            if changed > n:
                run.note(f"skipping {changed} updates: larger than the {n}-document collection")
                continue
            for i in range(args.samples):
                name = f"u{changed}-{i}"
                t0 = time.monotonic()
                _, create_ms = run.cli("branch_create", "branches", "create", name, "-p", project, "--from", "main",
                                       "--output", "json")
                out, checkout_ms = run.cli("checkout", "checkout", "-p", project, "-b", name, "--output", "json")
                read_ms = first_read(out["connection_string"], f"item-{n - 1:08d}")
                total_ms = (time.monotonic() - t0) * 1000
                run.add("branch_create_ms", i, create_ms, changed=changed)
                run.add("checkout_ms", i, checkout_ms, changed=changed)
                run.add("first_read_ms", i, read_ms, changed=changed)
                run.add("new_branch_to_first_read_ms", i, total_ms, changed=changed)
                branch_id, branch_db = out["branch_id"], out["physical_db"]
                if "branch_checkout" not in result["storage"]:
                    result["storage"]["branch_checkout"] = db_size(client, branch_db)

                handle = MongoClient(out["connection_string"])
                items = handle.get_default_database().get_collection("items", write_concern=WriteConcern("majority"))
                if not point_reads_done:
                    ids = [f"item-{rng.randrange(n):08d}" for _ in range(args.point_reads)]
                    items.find_one({"_id": ids[0]})  # connection already warm; first sample is kept too
                    for j, wanted in enumerate(ids):
                        started = time.perf_counter_ns()
                        found = items.find_one({"_id": wanted})
                        micros = (time.perf_counter_ns() - started) / 1000
                        if not found:
                            raise RuntimeError("point read missed a seeded document")
                        run.add("point_read_by_id_us", j, micros, unit="us")
                    point_reads_done = True

                run.note(f"$ argon watch -p {project} -b {name} &")
                started = time.monotonic()
                watcher = subprocess.Popen([str(run.binary), "watch", "-p", project, "-b", name], env=run.env,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                watchers.append(watcher)
                ready = ""
                while "Watching for changes" not in ready:
                    ready = watcher.stdout.readline()
                    if not ready:
                        raise RuntimeError("argon watch exited before it was ready")
                    run.note(ready.rstrip("\n"))
                run.add("watch_ready_ms", i, (time.monotonic() - started) * 1000, changed=changed)

                chosen = [f"item-{k:08d}" for k in rng.sample(range(n), changed)]
                started = time.monotonic()
                written = items.bulk_write([UpdateOne({"_id": k}, {"$inc": {"qty": 1}}) for k in chosen], ordered=False)
                acknowledged = time.monotonic()
                if written.modified_count != changed:
                    raise RuntimeError(f"bulk update modified {written.modified_count}, want {changed}")
                run.add(f"bulk_update_{changed}_ms", i, (acknowledged - started) * 1000, changed=changed)
                query = {"branch_id": branch_id, "collection": "items", "operation": "put"}
                while client[meta].wal_log.count_documents(query) < changed:
                    if time.monotonic() - acknowledged > 600:
                        raise RuntimeError("capture did not record every update within 10 minutes")
                    time.sleep(.02)
                run.add(f"capture_after_ack_{changed}_ms", i, (time.monotonic() - acknowledged) * 1000, changed=changed)
                captured = client[meta].wal_log.count_documents(query)
                if captured != changed:
                    raise RuntimeError(f"captured {captured} records, want {changed}")
                handle.close()

                for repeat in range(args.diff_repeats):
                    plan, ms = run.cli("diff", "diff", "-p", project, "-b", name, "--output", "json")
                    plan = plan["plan"]
                    if len(plan["changes"] or []) != changed or plan["conflicts"]:
                        raise RuntimeError("diff does not list exactly the updated documents")
                    run.add(f"diff_{changed}_changed_ms", i * args.diff_repeats + repeat, ms, changed=changed)
                plan, preview_ms = run.cli("merge_preview", "merge", "preview", "-p", project, "-b", name, "--output", "json")
                plan = plan["plan"]
                if len(plan["changes"] or []) != changed or plan["conflicts"]:
                    raise RuntimeError("merge plan does not list exactly the updated documents")
                applied, apply_ms = run.cli("merge_apply", "merge", "apply", plan["id"], "--output", "json")
                if applied["applied"] != changed:
                    raise RuntimeError(f"merge applied {applied['applied']}, want {changed}")
                run.add(f"merge_preview_{changed}_changed_ms", i, preview_ms, changed=changed)
                run.add(f"merge_apply_{changed}_changed_ms", i, apply_ms, changed=changed)
                run.add(f"merge_preview_plus_apply_{changed}_changed_ms", i, preview_ms + apply_ms, changed=changed)
                for k in chosen:
                    expected_main[k] = expected_main.get(k, 0) + 1
                probe = chosen[0]
                if client[main_db].items.find_one({"_id": probe})["qty"] != expected_main[probe]:
                    raise RuntimeError("merged value is not in the checked-out main database")

                watcher.send_signal(signal.SIGINT)
                try:
                    watcher.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    watcher.kill()
                    watcher.wait(timeout=10)
                run.note(f"[argon watch stopped, exit {watcher.returncode}]")
                _, ms = run.cli("release", "release", "-p", project, "-b", name, "--output", "json")
                run.add("release_ms", i, ms, changed=changed)
                run.cli("branch_delete", "branches", "delete", name, "-p", project, parse=False)

        for i in range(args.samples):
            t0 = time.monotonic()
            box, create_ms = run.cli("sandbox_create", "sandbox", "create", "-p", project, "--output", "json")
            read_ms = first_read(box["connection_string"], f"item-{n - 1:08d}")
            run.add("sandbox_create_ms", i, create_ms)
            run.add("sandbox_first_read_ms", i, read_ms)
            run.add("sandbox_create_to_first_read_ms", i, (time.monotonic() - t0) * 1000)
            _, ms = run.cli("sandbox_discard", "sandbox", "discard", "-p", project, "-b", box["name"], "--output", "json")
            run.add("sandbox_discard_ms", i, ms)

        # Every merged update must be in main, and nothing else may have changed.
        total = sum(expected_main.values())
        pipeline = [{"$group": {"_id": None, "qty": {"$sum": "$qty"}, "docs": {"$sum": 1}}}]
        final = next(client[main_db].items.aggregate(pipeline))
        if final["docs"] != n or final["qty"] != total:
            raise RuntimeError(f"main holds {final['docs']} documents and {final['qty']} increments, want {n} and {total}")
        result["counts"] = {"merged_updates": total, "main_documents": final["docs"],
                            "wal_entries": client[meta].wal_log.estimated_document_count()}
        result["storage"]["metadata_at_end"] = db_size(client, meta)
    finally:
        for watcher in watchers:
            if watcher.poll() is None:
                watcher.kill()
                watcher.wait(timeout=10)
        drop_fixture(client, meta, source)
    by_operation: dict[str, list[float]] = {}
    for sample in run.samples:
        value = sample.get("ms", sample.get("us"))
        by_operation.setdefault(sample["operation"], []).append(value)
    result["samples"] = run.samples
    result["summaries"] = {op: summarize(values) for op, values in sorted(by_operation.items())}
    result["cli_peak_rss_kb"] = dict(run.cli_peak_rss_kb)
    return result


def drop_fixture(client: MongoClient, meta: str, source: str) -> None:
    """Drop only databases this scenario's own metadata names, then the fixture itself."""
    names = set(client.list_database_names())
    if meta in names:
        for branch in client[meta].wal_branches.find({}, {"physical_db": 1}):
            physical = branch.get("physical_db")
            if physical and physical.startswith("argon_br_") and physical in names:
                client.drop_database(physical)
    client.drop_database(source)
    client.drop_database(meta)


def markdown(report: dict) -> str:
    env, lines = report["environment"], []
    lines += [f"# Argon {report['version']} CLI workflow at {', '.join(str(s['documents']) for s in report['scenarios'])} documents", "",
              f"Window: `{report['started_at']}` → `{report['finished_at']}`. Complete: **{report['complete']}**.", "",
              f"Binary SHA256 `{report['binary_sha256']}`; MongoDB {env['mongodb_version']}; "
              f"WiredTiger cache {env['wiredtiger_cache_bytes'] / 2**30:.2f} GiB; {env['logical_cpus']} logical CPUs and "
              f"{env['memory_total_kb'] / 2**20:.1f} GiB visible to the measuring process.", "",
              "Each timing is wall clock around a whole CLI process or driver call. `n` is the number of samples; "
              "with few samples the maximum is the observed maximum, not a tail estimate.", ""]
    for sc in report["scenarios"]:
        lines += [f"## {sc['documents']} documents", "", "| Operation | n | min | p50 | p95 | max |", "|---|---:|---:|---:|---:|---:|"]
        for op, s in sc["summaries"].items():
            lines.append(f"| `{op}` | {s['n']} | {s['min']:.2f} | {s['p50']:.2f} | {s['p95']:.2f} | {s['max']:.2f} |")
        lines += ["", "| Database | Documents | Logical data bytes | Allocated storage bytes | Allocated index bytes |", "|---|---:|---:|---:|---:|"]
        for label, s in sc["storage"].items():
            lines.append(f"| {label} | {s['objects']} | {s['logical_data_bytes']} | {s['allocated_storage_bytes']} | {s['allocated_index_bytes']} |")
        lines += ["", "Largest peak resident memory of one CLI process, by command (kB):", ""]
        lines += [f"- `{label}`: {kb}" for label, kb in sc["cli_peak_rss_kb"].items()]
        lines += ["", f"Merged updates verified in main: {sc['counts'].get('merged_updates')}; WAL entries at the end: {sc['counts'].get('wal_entries')}.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--binary", type=Path, required=True, help="published argon executable")
    parser.add_argument("--version", required=True, help="version the binary must report")
    parser.add_argument("--sizes", default="10000,100000,1000000", help="comma-separated document counts")
    parser.add_argument("--update-sizes", default="100,10000", help="documents updated on each branch before diff and merge")
    parser.add_argument("--samples", type=int, default=5, help="branch workflows per document count and update size")
    parser.add_argument("--diff-repeats", type=int, default=3, help="diff commands per branch workflow")
    parser.add_argument("--point-reads", type=int, default=1000, help="point reads by _id per document count")
    parser.add_argument("--host-info", type=Path, help="JSON describing the host, recorded verbatim")
    parser.add_argument("--output", type=Path, required=True, help="new directory for raw.json, report.md and commands.log")
    args = parser.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    args.update_sizes = [int(s) for s in args.update_sizes.split(",")]
    if min(sizes + args.update_sizes + [args.samples, args.diff_repeats, args.point_reads]) < 1:
        parser.error("sizes, update sizes and sample counts must be positive")
    binary = args.binary.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/?replicaSet=rs0")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    hello = client.admin.command("hello")
    assert hello.get("setName"), "a replica set is required"
    reported = subprocess.run([str(binary), "--version"], capture_output=True, text=True, check=True).stdout.strip()
    if reported.split()[-1] != args.version:
        raise SystemExit(f"binary reports {reported!r}, expected version {args.version}")
    status = client.admin.command("serverStatus")
    memory_kb = next((int(line.split()[1]) for line in Path("/proc/meminfo").read_text().splitlines()
                      if line.startswith("MemTotal:")), 0) if Path("/proc/meminfo").exists() else 0
    environment = {
        "mongodb_version": client.server_info()["version"], "replica_set": hello["setName"],
        "replica_member_count": len(client.admin.command("replSetGetConfig")["config"]["members"]),
        "mongodb_storage_engine": status["storageEngine"]["name"],
        "wiredtiger_cache_bytes": int(status["wiredTiger"]["cache"]["maximum bytes configured"]),
        "platform": platform.platform(), "machine": platform.machine(), "python": platform.python_version(),
        "logical_cpus": os.cpu_count(), "memory_total_kb": memory_kb,
        "write_concern": "seed and measured native writes: majority",
        "timing": "monotonic wall clock around whole CLI processes and driver calls; no warm-up discarded; one workflow at a time",
        "isolation": "shared developer host; background load is not controlled",
        "host": json.loads(args.host_info.read_text()) if args.host_info else None,
    }
    report = {"schema_version": 1, "kind": "cli-scale", "version": args.version, "reported_version": reported,
              "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
              "config": {"sizes": sizes, "update_sizes": args.update_sizes, "samples": args.samples,
                         "diff_repeats": args.diff_repeats, "point_reads": args.point_reads,
                         "document": "string _id item-%08d, name, qty, price, category, 128-byte payload; one collection, _id index only"},
              "environment": environment, "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "scenarios": [], "skipped": [], "complete": False}
    try:
        with (args.output / "commands.log").open("w") as log:
            run = Runner(binary, uri, log, client)
            run.note(f"{reported}; binary sha256 {report['binary_sha256']}; MongoDB {environment['mongodb_version']}")
            for n in sizes:
                print(f"scenario documents={n}", flush=True)
                try:
                    report["scenarios"].append(scenario(run, n, args))
                except Exception as error:  # record why a size could not be measured, then stop
                    report["skipped"].append({"documents": n, "error_type": type(error).__name__, "error": str(error)[:2000]})
                    run.note(f"SCENARIO FAILED: {type(error).__name__}: {error}")
                    raise
            report["complete"] = True
    finally:
        report["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (args.output / "raw.json").write_text(json.dumps(report, indent=2) + "\n")
        if report["scenarios"]:
            (args.output / "report.md").write_text(markdown(report))
        client.close()
    if not report["complete"]:
        raise SystemExit("run did not complete; inspect raw.json and commands.log")
    print(markdown(report))


if __name__ == "__main__":
    main()
