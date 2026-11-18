#!/usr/bin/env python3
"""Alternate two argon binaries on one project so that both see the same load.

  interleaved.py <documents> <rounds> <binary A> <binary B> [documents changed, default 100]

Seeds and imports once (with binary A), checks out main, then for each round and
each binary in turn: create a branch from main, check it out, update the chosen
number of documents through the driver with that binary's `argon watch` capturing,
run the first diff, a second diff and a merge preview, release and delete the branch. Prints one line per
measurement. PAUSE_BEFORE_SECOND_DIFF (seconds, default 0) waits between
the first and the second diff. Runs inside a container that shares MongoDB's network namespace.
"""
import json
import os
import signal
import subprocess
import sys
import time
import uuid

from pymongo import MongoClient, UpdateOne
from pymongo.write_concern import WriteConcern

N, ROUNDS = int(sys.argv[1]), int(sys.argv[2])
BINARIES = {"A": sys.argv[3], "B": sys.argv[4]}
CHANGED = int(sys.argv[5]) if len(sys.argv) > 5 else 100
URI = "mongodb://localhost:27017/?replicaSet=rs0"
client = MongoClient(URI)
suffix = uuid.uuid4().hex[:10]
meta, source, project = f"argonbench_il_meta_{suffix}", f"argonbench_il_src_{suffix}", "interleaved"
env = dict(os.environ, MONGODB_URI=URI, ARGON_METADATA_DB=meta)


def cli(binary, *args):
    started = time.monotonic()
    done = subprocess.run([binary, *args], env=env, capture_output=True, text=True)
    elapsed = (time.monotonic() - started) * 1000
    if done.returncode != 0:
        raise SystemExit(f"{binary} {' '.join(args)} failed: {done.stderr[-400:]}")
    return done.stdout, elapsed


for label, binary in BINARIES.items():
    print(f"binary {label}: {subprocess.run([binary, '--version'], capture_output=True, text=True).stdout.strip()}", flush=True)
items = client[source].get_collection("items", write_concern=WriteConcern("majority"))
for start in range(0, N, 1000):
    items.insert_many([{"_id": f"item-{i:08d}", "name": f"Item {i}", "qty": 0, "price": (i % 10000) / 100,
                        "category": f"cat-{i % 20}", "payload": "x" * 128} for i in range(start, min(N, start + 1000))])
cli(BINARIES["A"], "import", "database", "--uri", URI, "--database", source, "--project", project, "--source-quiesced", "--yes", "--output", "json")
cli(BINARIES["A"], "checkout", "-p", project, "-b", "main", "--output", "json")
print(f"{N} documents imported, main checked out, nothing watching main; {CHANGED} documents changed per branch", flush=True)

results = {label: {"checkout": [], "first_diff": [], "second_diff": [], "merge_preview": [], "create_to_first_diff_done": []} for label in BINARIES}
try:
    for round_number in range(ROUNDS):
        order = list(BINARIES) if round_number % 2 == 0 else list(BINARIES)[::-1]
        for label in order:
            binary, name = BINARIES[label], f"r{round_number}-{label.lower()}"
            t0 = time.monotonic()
            cli(binary, "branches", "create", name, "-p", project, "--from", "main", "--output", "json")
            out, checkout_ms = cli(binary, "checkout", "-p", project, "-b", name, "--output", "json")
            box = json.loads(out)
            watcher = subprocess.Popen([binary, "watch", "-p", project, "-b", name], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            while "Watching for changes" not in watcher.stdout.readline():
                pass
            branch = MongoClient(box["connection_string"]).get_default_database().get_collection("items", write_concern=WriteConcern("majority"))
            chosen = [f"item-{(round_number * 7919 + k * (N // CHANGED)) % N:08d}" for k in range(CHANGED)]
            branch.bulk_write([UpdateOne({"_id": k}, {"$inc": {"qty": 1}}) for k in chosen], ordered=False)
            query = {"branch_id": box["branch_id"], "collection": "items", "operation": "put"}
            while client[meta].wal_log.count_documents(query) < CHANGED:
                time.sleep(0.02)
            out, first_ms = cli(binary, "diff", "-p", project, "-b", name, "--output", "json")
            total_ms = (time.monotonic() - t0) * 1000
            plan = json.loads(out)["plan"]
            assert len(plan["changes"] or []) == CHANGED and not plan["conflicts"], "diff must list the updated documents"
            time.sleep(float(os.environ.get("PAUSE_BEFORE_SECOND_DIFF", "0")))
            print(f"  second diff of {label} starts {time.strftime('%H:%M:%S', time.gmtime())}.{int(time.time() % 1 * 1000):03d}Z", flush=True)
            _, second_ms = cli(binary, "diff", "-p", project, "-b", name, "--output", "json")
            print(f"  second diff of {label} ended {time.strftime('%H:%M:%S', time.gmtime())}.{int(time.time() % 1 * 1000):03d}Z", flush=True)
            _, preview_ms = cli(binary, "merge", "preview", "-p", project, "-b", name, "--output", "json")
            watcher.send_signal(signal.SIGINT)
            watcher.wait(timeout=30)
            cli(binary, "release", "-p", project, "-b", name, "--output", "json")
            cli(binary, "branches", "delete", name, "-p", project)
            r = results[label]
            r["checkout"].append(round(checkout_ms))
            r["first_diff"].append(round(first_ms))
            r["second_diff"].append(round(second_ms))
            r["merge_preview"].append(round(preview_ms))
            r["create_to_first_diff_done"].append(round(total_ms))
            print(f"round {round_number} binary {label}: checkout {checkout_ms:.0f} ms, first diff {first_ms:.0f} ms, second diff {second_ms:.0f} ms, merge preview {preview_ms:.0f} ms, branch create to first diff done {total_ms:.0f} ms", flush=True)
finally:
    for b in client[meta].wal_branches.find({}, {"physical_db": 1}):
        if b.get("physical_db", "").startswith("argon_br_"):
            client.drop_database(b["physical_db"])
    client.drop_database(source)
    client.drop_database(meta)
print("RESULTS " + json.dumps(results), flush=True)
