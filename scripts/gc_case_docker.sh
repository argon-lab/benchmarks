#!/usr/bin/env bash
# Time `argon diff` before and after `argon gc` deleted the parent's entries.
#   gc_case_docker.sh <argonctl version> <sizes, comma separated> <output file>
# MongoDB 7.0.45 (one-node replica set, 2 GiB cache) and a container with Argon
# from npm, sharing one network namespace; no published ports; both removed at the end.
set -uo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
VERSION="$1"; SIZES="$2"; OUT="$3"
cleanup() { docker rm -f argongc-runner argongc-mongo >/dev/null 2>&1; }
trap cleanup EXIT
{
  echo "date (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  docker run -d --name argongc-mongo 'mongo:7.0.45@sha256:c53852c00c23ca9f23fc39690350ffa9a80e3642fe8f96879726d8da0abe80a7' mongod --replSet rs0 --bind_ip_all --wiredTigerCacheSizeGB 2 >/dev/null
  for _ in $(seq 1 120); do
    docker exec argongc-mongo mongosh --quiet --eval 'try { rs.status() } catch (e) { rs.initiate({_id: "rs0", members: [{_id: 0, host: "localhost:27017"}]}) }; if (!db.hello().isWritablePrimary) quit(1)' >/dev/null 2>&1 && break
    sleep 1
  done
  docker run -d --name argongc-runner --network container:argongc-mongo node:24-bookworm sleep infinity >/dev/null
  docker exec argongc-runner bash -c 'apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq python3-venv >/dev/null 2>&1; python3 -m venv /root/venv && /root/venv/bin/pip install -q pymongo==4.20.0 2>&1 | tail -1'
  docker exec argongc-runner bash -c "npm install -g argonctl@$VERSION --allow-scripts=argonctl >/dev/null 2>&1"
  docker exec argongc-runner /usr/local/lib/node_modules/argonctl/bin/argon-bin --version
  docker cp -q "$S/gc_case.py" argongc-runner:/root/gc_case.py
  docker exec -e PYTHONUNBUFFERED=1 argongc-runner /root/venv/bin/python /root/gc_case.py /usr/local/lib/node_modules/argonctl/bin/argon-bin "$SIZES"
  echo "exit $?"
} > "$OUT" 2>&1
