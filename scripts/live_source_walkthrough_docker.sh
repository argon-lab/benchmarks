#!/usr/bin/env bash
# Run live_source_walkthrough.py against the npm release of Argon. Two MongoDB 7.0.45 one-member replica sets
# (the source and Argon's own) and a runner, on a private Docker network with no published
# ports. Everything is removed at the end.
#
#   live_source_walkthrough_docker.sh <argonctl version> <output directory> [ORDERS]
set -uo pipefail
VERSION="$1"; OUT="$2"; ORDERS="${3:-2000}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
NET=argon-wbpost-net
cleanup() { docker rm -f argon-wbpost-runner argon-wbpost-source argon-wbpost-meta >/dev/null 2>&1; docker network rm argon-wbpost-net >/dev/null 2>&1; }
trap cleanup EXIT
cleanup
docker network create "$NET" >/dev/null
IMAGE='mongo:7.0.45@sha256:c53852c00c23ca9f23fc39690350ffa9a80e3642fe8f96879726d8da0abe80a7'
docker run -d --name argon-wbpost-source --network "$NET" "$IMAGE" mongod --replSet src0 --bind_ip_all >/dev/null
docker run -d --name argon-wbpost-meta --network "$NET" "$IMAGE" mongod --replSet rs0 --bind_ip_all >/dev/null
for pair in argon-wbpost-source:src0 argon-wbpost-meta:rs0; do
  c="${pair%%:*}"; rs="${pair#*:}"
  for _ in $(seq 1 120); do
    docker exec "$c" mongosh --quiet --eval "try { rs.status() } catch (e) { rs.initiate({_id: '$rs', members: [{_id: 0, host: '$c:27017'}]}) }; if (!db.hello().isWritablePrimary) quit(1)" >/dev/null 2>&1 && break
    sleep 1
  done
done
docker run -d --name argon-wbpost-runner --network "$NET" -v "$OUT":/out node:24-bookworm sleep infinity >/dev/null
docker exec argon-wbpost-runner bash -c 'apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq python3-venv >/dev/null 2>&1; python3 -m venv /root/venv && /root/venv/bin/pip install -q pymongo==4.20.0 2>&1 | tail -1'
docker exec argon-wbpost-runner npm install -g "argonctl@$VERSION" --allow-scripts=argonctl >/dev/null 2>&1
docker cp -q "$HERE/live_source_walkthrough.py" argon-wbpost-runner:/root/live_source_walkthrough.py
docker exec -e PYTHONUNBUFFERED=1 -e ORDERS="$ORDERS" \
  -e SOURCE_URI='mongodb://argon-wbpost-source:27017/?replicaSet=src0' \
  -e MONGODB_URI='mongodb://argon-wbpost-meta:27017/?replicaSet=rs0' \
  argon-wbpost-runner /root/venv/bin/python /root/live_source_walkthrough.py > "$OUT/transcript.txt" 2>&1
status=$?
docker exec argon-wbpost-runner sha256sum /usr/local/lib/node_modules/argonctl/bin/argon-bin > "$OUT/binary-sha256.txt" 2>&1
exit $status
