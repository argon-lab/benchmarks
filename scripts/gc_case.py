#!/usr/bin/env python3
"""Time `argon diff` before and after `argon gc` has deleted the parent's entries.

Runs inside the runner container (see gc_case_docker.sh). For each size: seed, import,
check out main, create a branch, check it out, update 100 documents with
`argon watch` capturing, diff three times; then `argon gc` with a zero retention
window, and diff three times again. Prints every command, its output (shortened)
and its wall time and sampled peak memory.
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from pymongo import MongoClient, UpdateOne
from pymongo.write_concern import WriteConcern

BIN = sys.argv[1]
SIZES = [int(x) for x in sys.argv[2].split(",")]
URI = "mongodb://localhost:27017/?replicaSet=rs0"
client = MongoClient(URI)


def cli(env, *args):
    print(f"$ argon {' '.join(args)}", flush=True)
    started = time.monotonic()
    process = subprocess.Popen([BIN, *args], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    peak, status = 0, Path(f"/proc/{process.pid}/status")
    box = {}
    reader = threading.Thread(target=lambda: box.update(out=process.communicate()))
    reader.start()
    while reader.is_alive():
        try:
            for line in status.read_text().splitlines():
                if line.startswith("VmHWM:"):
                    peak = max(peak, int(line.split()[1]))
        except (OSError, ValueError):
            pass
        reader.join(0.02)
    elapsed = (time.monotonic() - started) * 1000
    out, err = box["out"]
    shown = out if len(out) <= 1500 else out[:700] + f"\n… {len(out) - 1400} characters omitted …\n" + out[-700:]
    print(shown.rstrip("\n"))
    for line in err.strip().splitlines():
        if "WAL Monitor" not in line:
            print("[stderr] " + line)
    print(f"[exit {process.returncode}, {elapsed:.1f} ms, sampled peak RSS {peak} kB]", flush=True)
    if process.returncode != 0:
        raise SystemExit(f"argon {' '.join(args)} failed")
    return out, elapsed, peak


for n in SIZES:
    suffix = uuid.uuid4().hex[:10]
    meta, source, project = f"argonbench_gc_meta_{suffix}", f"argonbench_gc_src_{suffix}", f"gc-{n}"
    env = dict(os.environ, MONGODB_URI=URI, ARGON_METADATA_DB=meta)
    print(f"\n===== {n} documents =====", flush=True)
    items = client[source].get_collection("items", write_concern=WriteConcern("majority"))
    for start in range(0, n, 1000):
        items.insert_many([{"_id": f"item-{i:08d}", "name": f"Item {i}", "qty": 0, "price": (i % 10000) / 100,
                            "category": f"cat-{i % 20}", "payload": "x" * 128} for i in range(start, min(n, start + 1000))])
    cli(env, "import", "database", "--uri", URI, "--database", source, "--project", project, "--source-quiesced", "--yes", "--output", "json")
    cli(env, "branches", "create", "work", "-p", project, "--from", "main", "--output", "json")
    out, _, _ = cli(env, "checkout", "-p", project, "-b", "work", "--output", "json")
    box = json.loads(out)
    watcher = subprocess.Popen([BIN, "watch", "-p", project, "-b", "work"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    while "Watching for changes" not in watcher.stdout.readline():
        pass
    branch = MongoClient(box["connection_string"]).get_default_database().get_collection("items", write_concern=WriteConcern("majority"))
    step = max(1, n // 100)
    chosen = [f"item-{i:08d}" for i in range(0, n, step)][:100]
    branch.bulk_write([UpdateOne({"_id": k}, {"$inc": {"qty": 1}}) for k in chosen], ordered=False)
    query = {"branch_id": box["branch_id"], "collection": "items", "operation": "put"}
    while client[meta].wal_log.count_documents(query) < 100:
        time.sleep(0.05)
    print("100 updates captured on the branch")
    results = {}
    for label in ("before gc", "after gc"):
        if label == "after gc":
            cli(env, "snapshot", "list", "-p", project, "-b", "main")
            cli(env, "gc", "-p", project, "--retention", "0s", "--output", "json")
            print("entries of main left in the log:", client[meta].wal_log.count_documents({"branch_id": {"$ne": box["branch_id"]}, "collection": "items"}))
        samples = []
        for _ in range(3):
            out, ms, peak = cli(env, "diff", "-p", project, "-b", "work", "--output", "json")
            plan = json.loads(out)["plan"]
            assert len(plan["changes"] or []) == 100 and not plan["conflicts"], "diff must list the 100 updated documents"
            samples.append((round(ms, 1), peak))
        results[label] = samples
        print(f"RESULT {n} documents, diff {label}: ms and peak kB per run: {samples}", flush=True)
    watcher.send_signal(signal.SIGINT)
    watcher.wait(timeout=30)
    for b in client[meta].wal_branches.find({}, {"physical_db": 1}):
        if b.get("physical_db", "").startswith("argon_br_"):
            client.drop_database(b["physical_db"])
    client.drop_database(source)
    client.drop_database(meta)
