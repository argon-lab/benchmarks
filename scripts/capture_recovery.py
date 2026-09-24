#!/usr/bin/env python3
"""Sustain native writes, kill only the spawned API, and verify capture recovery.

Requires pymongo and a disposable MongoDB 7+ replica set. The supplied release
CLI is started with a unique metadata database. No existing Argon project is
used. This is a correctness/soak experiment, not a performance SLA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import signal
import socket
import subprocess
import time
import urllib.request
import uuid

from pymongo import MongoClient
from pymongo.write_concern import WriteConcern


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--duration-seconds", type=int, default=600)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.duration_seconds < 60:
        parser.error("duration must be at least 60 seconds to cross health-check cycles")
    binary = args.binary.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/?replicaSet=rs0")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    assert client.admin.command("hello").get("setName"), "a replica set is required"
    meta = "argonbench_recovery_" + uuid.uuid4().hex[:12]
    project = "capture-recovery"
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    api_url = f"http://127.0.0.1:{port}"
    env = dict(os.environ, MONGODB_URI=uri, ARGON_METADATA_DB=meta,
               ARGON_API_HOST="127.0.0.1")
    for name in ("ARGON_DEMO_MODE", "ARGON_API_TOKEN", "ARGON_READ_ONLY"):
        env.pop(name, None)
    process = None
    physical = None
    db_client = None
    log = (args.output / "api.log").open("w")

    def call(method, path, body=None):
        request = urllib.request.Request(api_url + path, method=method,
                                         data=json.dumps(body).encode() if body is not None else None,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=40) as response:
            return json.load(response)

    def start():
        nonlocal process
        process = subprocess.Popen([str(binary), "console", "--port", str(port), "--no-browser"],
                                   env=env, stdout=log, stderr=subprocess.STDOUT)
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError("API exited during startup; inspect api.log")
            try:
                info = call("GET", "/api/v1/meta")
                if info["version"] != args.version:
                    raise RuntimeError(f"wrong release version: {info['version']}")
                return
            except (OSError, ValueError):
                time.sleep(.25)
        raise RuntimeError("API did not become healthy")

    began = time.monotonic()
    samples = []
    report = {"version": args.version, "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
              "mongodb_version": client.server_info()["version"], "host": platform.platform(),
              "python_version": platform.python_version(), "duration_requested_seconds": args.duration_seconds,
              "complete": False, "scope": "one native writer; local API crash/restart; no MongoDB failover or disk-loss simulation"}
    try:
        start()
        call("POST", "/api/v1/projects", {"name": project})
        box = call("POST", f"/api/v1/projects/{project}/sandboxes",
                   {"name": "soak", "ttl_minutes": max(30, args.duration_seconds // 60 + 10), "actor": "benchmark:recovery"})
        db_client = MongoClient(box["connection_string"], w="majority")
        database = db_client.get_default_database()
        physical = database.name
        database.create_collection("counters", changeStreamPreAndPostImages={"enabled": True})
        collection = database.get_collection("counters", write_concern=WriteConcern("majority"))
        collection.insert_one({"_id": "counter", "value": 0})
        prefix = f"/api/v1/projects/{project}/branches/{box['branch']}"
        value = 0
        restarted = False
        verified = 0

        def check():
            nonlocal verified
            barrier_at = time.monotonic()
            call("GET", prefix + "/diff")  # capture barrier, including after restart
            barrier_ms = (time.monotonic() - barrier_at) * 1000
            branch = call("GET", prefix)["branch"]
            captured = client[meta].wal_log.count_documents({"branch_id": branch["id"],
                                                           "collection": "counters", "document_id": "counter", "operation": "put"})
            if captured != value + 1:
                raise RuntimeError(f"history loss/duplication: captured={captured}, expected={value + 1}")
            state = call("GET", prefix + "/time-travel/query?collection=counters")
            if state["documents"][0]["value"] != value:
                raise RuntimeError("versioned state differs from acknowledged native writes")
            samples.append({"elapsed_seconds": time.monotonic() - began,
                            "expected_value": value, "captured_records": captured,
                            "diff_barrier_ms": barrier_ms,
                            "after_restart": restarted})
            verified += 1

        check()
        while time.monotonic() - began < args.duration_seconds:
            value += 1
            collection.update_one({"_id": "counter"}, {"$set": {"value": value}})
            check()
            if not restarted and time.monotonic() - began >= args.duration_seconds / 2:
                process.kill()  # only the process created by start(), never a discovered server
                process.wait(timeout=10)
                value += 1
                collection.update_one({"_id": "counter"}, {"$set": {"value": value}})
                restart_at = time.monotonic()
                start()
                restarted = True
                check()
                report["restart_to_verified_seconds"] = time.monotonic() - restart_at
            time.sleep(.25)
        assert restarted
        check()
        report.update(complete=True, native_writes=value + 1, verified_barriers=verified,
                      elapsed_seconds=time.monotonic() - began, crash_recovery_verified=True)
    except BaseException as error:
        report.update(complete=False, error_type=type(error).__name__)
        raise
    finally:
        cleanup_errors = []
        try:
            if process and process.poll() is None:
                stopped = time.monotonic()
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=15)
                    report["graceful_shutdown_seconds"] = time.monotonic() - stopped
                    report["graceful_shutdown_exit_code"] = process.returncode
                    if process.returncode != 0:
                        report["complete"] = False
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                    report.update(complete=False, graceful_shutdown_timeout=True)
            elif process:
                report.update(complete=False, unexpected_api_exit_code=process.returncode)
        except Exception as error:
            cleanup_errors.append({"step": "stop_api", "error_type": type(error).__name__})
        for step, cleanup in [
            ("close_log", log.close),
            ("drop_physical", lambda: client.drop_database(physical) if physical else None),
            ("drop_metadata", lambda: client.drop_database(meta)),
            ("close_native_client", lambda: db_client.close() if db_client else None),
            ("close_metadata_client", client.close),
        ]:
            try:
                cleanup()
            except Exception as error:
                cleanup_errors.append({"step": step, "error_type": type(error).__name__})
        if cleanup_errors:
            report.update(complete=False, cleanup_errors=cleanup_errors)
        (args.output / "recovery.json").write_text(json.dumps(report, indent=2) + "\n")
        (args.output / "recovery-samples.json").write_text(json.dumps(samples, indent=2) + "\n")
    if not report["complete"]:
        raise SystemExit("recovery/soak validation failed; inspect recovery.json and api.log")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
