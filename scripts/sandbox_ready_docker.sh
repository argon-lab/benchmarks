#!/usr/bin/env bash
# Run scripts/sandbox_ready.py against the npm release of Argon, with the CLI and
# MongoDB in two containers that share one network namespace. Nothing is
# published on the host's ports. The containers are created and removed here.
#
#   scripts/sandbox_ready_docker.sh <argonctl version> <new results directory> [sandbox_ready.py flags]
#
# WIREDTIGER_CACHE_GB (default 2) sets mongod's cache.
set -euo pipefail
VERSION="${1:?argonctl version, for example 2.4.0}"
RESULTS="${2:?new results directory}"
shift 2
SUITE="$(cd "$(dirname "$0")/.." && pwd)"
MONGO_IMAGE='mongo:7.0.45@sha256:c53852c00c23ca9f23fc39690350ffa9a80e3642fe8f96879726d8da0abe80a7'
RUNNER_IMAGE='node:24-bookworm'
PYMONGO_VERSION='4.20.0'
CACHE_GB="${WIREDTIGER_CACHE_GB:-2}"
BIN=/usr/local/lib/node_modules/argonctl/bin/argon-bin

[ ! -e "$RESULTS" ] || { echo "results directory already exists: $RESULTS" >&2; exit 1; }
if docker ps -a --format '{{.Names}}' | grep -q -E '^argonbench-ready-(mongo|runner)$'; then
  echo "containers from an earlier run exist; remove argonbench-ready-mongo and argonbench-ready-runner first" >&2
  exit 1
fi
mkdir -p "$RESULTS"
RESULTS="$(cd "$RESULTS" && pwd)"
cleanup() { [ -z "${LOAD_SAMPLER:-}" ] || kill "$LOAD_SAMPLER" 2>/dev/null || true; docker rm -fv argonbench-ready-runner argonbench-ready-mongo >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run -d --name argonbench-ready-mongo "$MONGO_IMAGE" \
  mongod --replSet rs0 --bind_ip_all --wiredTigerCacheSizeGB "$CACHE_GB" >/dev/null
for _ in $(seq 1 120); do
  docker exec argonbench-ready-mongo mongosh --quiet --eval \
    'try { rs.status() } catch (e) { rs.initiate({_id: "rs0", members: [{_id: 0, host: "localhost:27017"}]}) }; if (!db.hello().isWritablePrimary) quit(1)' \
    >/dev/null 2>&1 && break
  sleep 1
done
docker exec argonbench-ready-mongo mongosh --quiet --eval 'if (!db.hello().isWritablePrimary) quit(1)' >/dev/null

docker run -d --name argonbench-ready-runner --network container:argonbench-ready-mongo "$RUNNER_IMAGE" sleep infinity >/dev/null
docker exec argonbench-ready-runner bash -c 'apt-get update -qq >/dev/null && apt-get install -y -qq python3-venv >/dev/null'
docker exec argonbench-ready-runner bash -c "python3 -m venv /root/venv && /root/venv/bin/pip install -q pymongo==$PYMONGO_VERSION"
docker exec argonbench-ready-runner npm install -g "argonctl@$VERSION" --allow-scripts=argonctl >/dev/null
# The npm launcher starts this binary; it is measured directly so the launcher's
# Node start-up is not part of any timing. Its hash must be the one the package ships.
docker exec argonbench-ready-runner bash -c "
  set -e
  arch=\$(uname -m); case \$arch in aarch64) arch=arm64 ;; x86_64) arch=amd64 ;; esac
  want=\$(python3 -c \"import json; print(json.load(open('/usr/local/lib/node_modules/argonctl/checksums.json'))['argon-linux-\$arch'])\")
  got=\$(sha256sum $BIN | cut -d' ' -f1)
  [ \"\$want\" = \"\$got\" ] || { echo \"binary hash \$got differs from the package checksum \$want\" >&2; exit 1; }
"

python3 - "$SUITE" "$VERSION" "$MONGO_IMAGE" "$RUNNER_IMAGE" "$CACHE_GB" > "$RESULTS/provenance.json" <<'PY'
import hashlib, json, platform, subprocess, sys
from pathlib import Path
suite, version, mongo_image, runner_image, cache_gb = sys.argv[1:6]
def sh(*command):
    try:
        done = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:  # git and npm on the host are optional
        return None
    return done.stdout.strip() if done.returncode == 0 else None
def runner(command):
    return sh("docker", "exec", "argonbench-ready-runner", "bash", "-c", command)
host = {"platform": platform.platform(), "machine": platform.machine()}
for key in ("machdep.cpu.brand_string", "hw.memsize", "hw.ncpu", "kern.osproductversion"):
    value = sh("sysctl", "-n", key)
    if value:
        host[key] = value
docker = json.loads(sh("docker", "info", "--format", "{{json .}}") or "{}")
package = "/usr/local/lib/node_modules/argonctl"
print(json.dumps({
    "schema_version": 1,
    "suite": {"git_head": sh("git", "-C", suite, "rev-parse", "HEAD"),
              "dirty": bool(sh("git", "-C", suite, "status", "--porcelain", "--", "scripts")),
              "scripts_sha256": {name: hashlib.sha256((Path(suite) / "scripts" / name).read_bytes()).hexdigest()
                                 for name in ("sandbox_ready.py", "sandbox_ready_docker.sh", "cli_scale.py")}},
    "argon": {"npm_package": f"argonctl@{version}",
              "npm_dist_integrity": sh("npm", "view", f"argonctl@{version}", "dist.integrity"),
              "reported_version": runner(f"{package}/bin/argon-bin --version"),
              "binary": "bin/argon-bin, the executable the npm launcher starts",
              "binary_sha256": runner(f"sha256sum {package}/bin/argon-bin | cut -d' ' -f1"),
              "package_checksums": json.loads(runner(f"cat {package}/checksums.json"))},
    "runner": {"image": runner_image, "image_digest": sh("docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", runner_image),
               "node": runner("node --version"), "npm": runner("npm --version"), "python": runner("python3 --version"),
               "pymongo": runner("/root/venv/bin/python -c 'import pymongo; print(pymongo.version)'"),
               "network": "shares the MongoDB container's network namespace; MongoDB is reached at localhost:27017"},
    "mongodb": {"image": mongo_image, "command": f"mongod --replSet rs0 --bind_ip_all --wiredTigerCacheSizeGB {cache_gb}",
                "published_ports": "none"},
    "host": host,
    "docker": {key: docker.get(key) for key in ("ServerVersion", "OperatingSystem", "OSType", "Architecture", "NCPU", "MemTotal", "KernelVersion")},
}, indent=2))
PY

docker exec argonbench-ready-runner mkdir -p /suite/scripts
docker cp -q "$SUITE/scripts/sandbox_ready.py" argonbench-ready-runner:/suite/scripts/sandbox_ready.py
docker cp -q "$SUITE/scripts/cli_scale.py" argonbench-ready-runner:/suite/scripts/cli_scale.py
# The host is shared: sample its load and every running container while the suite runs.
( while :; do { date -u +%FT%TZ; uptime; docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}'; echo; } >> "$RESULTS/host-load.log" 2>&1; sleep 30; done ) &
LOAD_SAMPLER=$!; disown "$LOAD_SAMPLER"
docker cp -q "$RESULTS/provenance.json" argonbench-ready-runner:/suite/host-info.json
status=0
docker exec -e MONGODB_URI='mongodb://localhost:27017/?replicaSet=rs0' -e PYTHONUNBUFFERED=1 argonbench-ready-runner \
  /root/venv/bin/python /suite/scripts/sandbox_ready.py --binary "$BIN" --version "$VERSION" \
  --host-info /suite/host-info.json --output /suite/out "$@" || status=$?
docker cp -q argonbench-ready-runner:/suite/out/. "$RESULTS/" || true
docker logs argonbench-ready-mongo > "$RESULTS/mongod.log" 2>&1 || true
exit "$status"
