#!/usr/bin/env python3
"""Online import -> follow -> sandbox -> review -> write-back, on a source that keeps being written.

Runs inside a container that can reach two MongoDB 7.0 one-member replica sets:
SOURCE_URI (the "production" database) and MONGODB_URI (Argon's metadata and sandboxes).
Every argon command and its output is printed, with the time it took. A thread plays the
application: it inserts new orders and updates existing ones on the source for the whole
run, except while a comparison needs the source to stand still (said in the output).

Orders 1..99 are never touched by the application thread, so the reviewed changes and the
deliberate concurrent edit are the only writes to them.
"""
import datetime
import hashlib
import json
import os
import random
import re
import signal
import subprocess
import sys
import threading
import time

import bson
import bson.json_util
import bson.raw_bson
from pymongo import MongoClient
from pymongo.write_concern import WriteConcern

ARGON = os.environ.get("ARGON", "argon")
SOURCE_URI = os.environ["SOURCE_URI"]
ARGON_URI = os.environ["MONGODB_URI"]
N = int(os.environ.get("ORDERS", "2000"))
ENV = dict(os.environ, ARGON_SOURCE_URI=SOURCE_URI)
source = MongoClient(SOURCE_URI)
shop = source["shop"]
orders = shop.get_collection("orders", write_concern=WriteConcern("majority"))
rng = random.Random(7)
INTERVAL = float(os.environ.get("WRITE_INTERVAL_SECONDS", "0.005"))


def say(text=""):
    print(text, flush=True)


def run(*args, expect=0, env=ENV, quiet=False):
    started = time.monotonic()
    done = subprocess.run([ARGON, *args], env=env, capture_output=True, text=True)
    ms = (time.monotonic() - started) * 1000
    if not quiet:
        say(f"\n$ argon {' '.join(args)}")
        if done.stdout.strip():
            say(done.stdout.rstrip())
        if done.stderr.strip():
            say("[stderr] " + done.stderr.rstrip().replace("\n", "\n[stderr] "))
        say(f"[exit {done.returncode}, {ms:.0f} ms]")
    if expect is not None and done.returncode != expect and not (expect == "nonzero" and done.returncode != 0):
        say(f"UNEXPECTED exit {done.returncode}: {done.stdout[-2000:]} {done.stderr[-2000:]}")
        raise SystemExit(1)
    return done


class App(threading.Thread):
    """The application: one write to the source, then a pause of INTERVAL seconds."""

    def __init__(self):
        super().__init__(daemon=True)
        self.running = threading.Event()
        self.running.set()
        self.stop = False
        self.inserts = self.updates = 0
        self.next_id = 900000
        self.idle = threading.Event()

    def run(self):
        while not self.stop:
            if not self.running.is_set():
                self.idle.set()
                time.sleep(0.01)
                continue
            self.idle.clear()
            if rng.random() < 0.4:
                self.next_id += 1
                orders.insert_one(order(self.next_id))
                self.inserts += 1
            else:
                k = rng.randrange(100, N + 1)
                orders.update_one({"_id": f"order-{k:06d}"}, {"$inc": {"touches": 1}, "$set": {"status": rng.choice(["paid", "packed", "shipped"])}})
                self.updates += 1
            time.sleep(INTERVAL)

    def pause(self):
        self.running.clear()
        self.idle.wait()

    def resume(self):
        self.running.set()

    @property
    def writes(self):
        return self.inserts + self.updates


def order(i):
    return {"_id": f"order-{i:06d}", "status": "paid", "customer": f"cust-{i % 200:03d}", "total_cents": 500 + (i * 37) % 20000,
            "items": [{"sku": f"sku-{i % 50:02d}", "qty": 1 + i % 3}], "placed_at": datetime.datetime(2026, 11, 1) + datetime.timedelta(minutes=i),
            "touches": 0}


def fingerprint(collection):
    """Count, a hash over every document's exact BSON bytes in _id order, and a hash over the
    same documents with the fields of every document sorted by name (values only, not order)."""
    exact, values, count = hashlib.sha256(), hashlib.sha256(), 0
    for raw in collection.with_options(codec_options=bson.codec_options.CodecOptions(document_class=bson.raw_bson.RawBSONDocument)).find().sort("_id", 1):
        exact.update(raw.raw)
        values.update(bson.json_util.dumps(bson.decode(raw.raw), sort_keys=True, json_options=bson.json_util.CANONICAL_JSON_OPTIONS).encode())
        count += 1
    return count, exact.hexdigest()[:16], values.hexdigest()[:16]


def compare(name, other, label):
    """Compare a source collection with another; report bytes and values separately."""
    a, b = fingerprint(shop[name]), fingerprint(other[name])
    same_bytes, same_values = a[:2] == b[:2], (a[0], a[2]) == (b[0], b[2])
    say(f"[{name}: source {a[0]} documents, {label} {b[0]} documents; values {'IDENTICAL' if same_values else 'DIFFERENT'} "
        f"(sha256 {a[2]} / {b[2]}); exact BSON bytes {'IDENTICAL' if same_bytes else 'DIFFERENT'} (sha256 {a[1]} / {b[1]})]")
    if not same_bytes:
        raw = bson.codec_options.CodecOptions(document_class=bson.raw_bson.RawBSONDocument)
        theirs = {bson.decode(d.raw)["_id"]: d.raw for d in other[name].with_options(codec_options=raw).find()}
        differing = [(bson.decode(d.raw), bson.decode(theirs[bson.decode(d.raw)["_id"]])) for d in shop[name].with_options(codec_options=raw).find()
                     if bson.decode(d.raw)["_id"] in theirs and theirs[bson.decode(d.raw)["_id"]] != d.raw]
        say(f"[{len(differing)} documents differ in bytes; the first: source fields {list(differing[0][0])}, {label} fields {list(differing[0][1])}]")
        say(f"[  source: {bson.json_util.dumps(differing[0][0])}]")
        say(f"[  {label}: {bson.json_util.dumps(differing[0][1])}]")
    assert same_values
    return same_bytes


def wait_for_main(since_writes_done, timeout=90):
    """Wait until following has stored a source time at or after the source's newest write."""
    newest = source.admin.command("hello")["lastWrite"]["opTime"]["ts"]
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() < deadline:
        last = run("source", "status", "-p", "shop", expect=None, quiet=True).stdout
        at = re.search(r"Consistent:\s+LSN \d+ is the source at Timestamp\((\d+), (\d+)\)", last)
        if at and "healthy (exact)" in last and (int(at.group(1)), int(at.group(2))) >= (newest.time, newest.inc):
            return time.monotonic() - since_writes_done
        time.sleep(0.25)
    say(last)
    raise SystemExit("following did not catch up in time")


def sandbox(name):
    proc = subprocess.Popen([ARGON, "sandbox", "create", "-p", "shop", "--name", name, "--watch", "--actor", name], env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    say(f"\n$ argon sandbox create -p shop --name {name} --watch --actor {name}    (left running)")
    uri, lines = None, []
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        line = proc.stdout.readline()
        if not line:
            break
        lines.append(line.rstrip())
        say(line.rstrip())
        for word in line.split():
            if word.startswith("mongodb://"):
                uri = word
        if uri and ("Watching" in line or "capturing" in line.lower() or "Ctrl" in line):
            break
    if not uri:
        raise SystemExit("no sandbox connection string in: " + "\n".join(lines))
    return proc, uri


def wait_for_diff(name, want):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        out = run("diff", "-p", "shop", "-b", name, "-o", "json", expect=None, quiet=True).stdout
        try:
            plan = json.loads(out)["plan"]
            if len(plan.get("changes") or []) == want:
                return
        except Exception:
            pass
        time.sleep(0.3)
    raise SystemExit(f"sandbox {name} did not show {want} captured changes")


def keys_of(doc_id):
    return list(shop.orders.find_one({"_id": doc_id}).keys())


say(f"== {datetime.datetime.utcnow():%Y-%m-%dT%H:%M:%SZ}")
say(run("--version", quiet=True).stdout.strip())
say("source: " + str(source.admin.command("buildInfo")["version"]) + ", replica set " + source.admin.command("hello")["setName"]
    + "; Argon metadata: " + MongoClient(ARGON_URI).admin.command("hello")["setName"] + " (a separate deployment)")
if os.environ.get("CLEAN_SOURCE") == "1":
    # A shared source (an Atlas cluster) may still hold an earlier run's shop.
    for name in shop.list_collection_names():
        shop[name].drop()
orders.insert_many([order(i) for i in range(1, N + 1)])
shop.get_collection("customers", write_concern=WriteConcern("majority")).insert_many([{"_id": f"cust-{i:03d}", "name": f"Customer {i}", "tier": "standard"} for i in range(200)])
say(f"seeded shop.orders with {N} documents and shop.customers with 200")

app = App()
app.start()
time.sleep(1)
say(f"the application thread is writing to the source (one write, then {INTERVAL * 1000:.0f} ms of sleep, for the whole run)")

say("\n##### 1. Import while the source is being written")
run("import", "preview", "--database", "shop", "--online")
before = app.writes
t0 = time.monotonic()
run("import", "database", "--database", "shop", "--project", "shop", "--online", "--yes")
say(f"[the application made {app.writes - before} writes to the source while this command ran ({time.monotonic() - t0:.1f} s)]")

say("\n##### 2. Follow")
follower = subprocess.Popen([ARGON, "source", "follow", "-p", "shop"], env=ENV, stdout=open("/out/follow.log", "w"), stderr=subprocess.STDOUT)
say("\n$ argon source follow -p shop    (left running; its output is in follow.log)")
time.sleep(8)
run("source", "status", "-p", "shop")

say("\n##### 3. Is main the source? (the application is paused for this comparison only)")
app.pause()
paused_at = time.monotonic()
waited = wait_for_main(paused_at)
say(f"[application paused; following stored the source's newest write {waited:.1f} s after it was made, on an otherwise idle source]")
run("source", "status", "-p", "shop")
check_proc, check_uri = sandbox("check")
check_db = MongoClient(check_uri).get_default_database()
for name in ("orders", "customers"):
    compare(name, check_db, "sandbox forked from main")
check_proc.send_signal(signal.SIGINT)
check_proc.wait(timeout=60)
run("sandbox", "discard", "-p", "shop", "-b", "check", expect=None)
app.resume()
say("[application resumed]")

say("\n##### 4. An agent works in a sandbox")
agent_proc, agent_uri = sandbox("agent-1")
agent = MongoClient(agent_uri).get_default_database().get_collection("orders", write_concern=WriteConcern("majority"))
say("[field order of order-000042 on the source before: " + ", ".join(keys_of("order-000042")) + "]")
agent.update_one({"_id": "order-000042"}, {"$set": {"status": "refunded", "refund_cents": 2054}})
agent.insert_one({"_id": "order-000042-refund", "status": "refund", "customer": "cust-042", "total_cents": -2054, "refunds": "order-000042"})
agent.delete_one({"_id": "order-000017"})
say("[the agent, through the sandbox's connection string: set order-000042 to refunded, inserted order-000042-refund, deleted order-000017]")
wait_for_diff("agent-1", 3)
run("diff", "-p", "shop", "-b", "agent-1")

say("\n##### 5. Review")
preview = run("merge", "preview", "-p", "shop", "-b", "agent-1", "-o", "json")
plan = json.loads(preview.stdout)["plan"]
plan_id, digest = plan["id"], plan["approval_digest"]

say("\n##### 6. What is refused")
writes_before = app.writes
state_before = {k: shop.orders.find_one({"_id": k}) for k in ("order-000042", "order-000042-refund", "order-000017")}
run("merge", "apply", plan_id, "--write-back", expect="nonzero")
run("merge", "apply", plan_id, "--write-back", "--approve", "0" * 64, expect="nonzero")
run("merge", "apply", plan_id, "--write-back", "--approve", digest, "--uri", ARGON_URI, expect="nonzero")
run("merge", "apply", plan_id, expect="nonzero")
assert state_before == {k: shop.orders.find_one({"_id": k}) for k in state_before}
say("[after the four refusals the three documents on the source are as they were]")

say("\n##### 7. Write back")
total_before = shop.orders.count_documents({})
run("merge", "apply", plan_id, "--write-back", "--approve", digest)
say("[on the source now]")
for k in ("order-000042", "order-000042-refund", "order-000017"):
    say(f"  {k}: {json.dumps(shop.orders.find_one({'_id': k}), default=str)}")
say("[field order of order-000042 on the source after: " + ", ".join(keys_of("order-000042")) + "]")
run("merge", "apply", plan_id, "--write-back", "--approve", digest, expect="nonzero")
time.sleep(6)
run("merge", "list", "-p", "shop")
run("source", "status", "-p", "shop")
agent_proc.send_signal(signal.SIGINT)
agent_proc.wait(timeout=60)

say("\n##### 8. Someone changes a reviewed document before the write-back")
agent2_proc, agent2_uri = sandbox("agent-2")
agent2 = MongoClient(agent2_uri).get_default_database().get_collection("orders", write_concern=WriteConcern("majority"))
agent2.update_one({"_id": "order-000050"}, {"$set": {"status": "cancelled"}})
agent2.update_one({"_id": "order-000051"}, {"$set": {"status": "cancelled"}})
say("[the agent set order-000050 and order-000051 to cancelled in its sandbox]")
wait_for_diff("agent-2", 2)
plan2 = json.loads(run("merge", "preview", "-p", "shop", "-b", "agent-2", "-o", "json", quiet=True).stdout)["plan"]
say(f"\n$ argon merge preview -p shop -b agent-2 -o json    (plan {plan2['id']}, {len(plan2['changes'])} changes, approval_digest {plan2['approval_digest']})")
orders.update_one({"_id": "order-000051"}, {"$set": {"status": "shipped", "tracking": "ZX-51"}})
say("[after the review, directly on the source: order-000051 set to shipped with a tracking number]")
run("merge", "apply", plan2["id"], "--write-back", "--approve", plan2["approval_digest"], expect="nonzero")
for k in ("order-000050", "order-000051"):
    say(f"  {k} on the source: {json.dumps(shop.orders.find_one({'_id': k}), default=str)}")
assert shop.orders.find_one({"_id": "order-000050"})["status"] == "paid"
run("merge", "list", "-p", "shop")
wait_for_main(time.monotonic())
say("[following has stored the concurrent edit; preview again]")
run("merge", "preview", "-p", "shop", "-b", "agent-2", expect=None)
agent2_proc.send_signal(signal.SIGINT)
agent2_proc.wait(timeout=60)

say("\n##### 9. Totals")
app.pause()
expected = N + app.inserts + 1 - 1
say(f"[application stopped after {app.inserts} inserts and {app.updates} updates in all; {app.writes - writes_before} of them after the review of the first plan]")
say(f"[shop.orders on the source: {shop.orders.count_documents({})} documents; expected {N} seeded + {app.inserts} inserted by the application + 1 inserted by the plan - 1 deleted by the plan = {expected}]")
assert shop.orders.count_documents({}) == expected
waited = wait_for_main(time.monotonic())
final_proc, final_uri = sandbox("final-check")
final_db = MongoClient(final_uri).get_default_database()
same = compare("orders", final_db, "a new sandbox forked from main")
final_proc.send_signal(signal.SIGINT)
final_proc.wait(timeout=60)
follower.send_signal(signal.SIGINT)
follower.wait(timeout=60)
run("source", "status", "-p", "shop", expect=None)
app.stop = True
if os.environ.get("CLEAN_SOURCE") == "1":
    app.join(timeout=10)
    for name in shop.list_collection_names():
        shop[name].drop()
    say("[the source's shop collections were dropped]")
say(f"\n== finished {datetime.datetime.utcnow():%Y-%m-%dT%H:%M:%SZ}")
