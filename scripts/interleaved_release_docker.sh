#!/usr/bin/env bash
# Alternate two npm releases of Argon on one project (interleaved.py), so both see the
# same background load. MongoDB 7.0.45, one-node replica set, 2 GiB cache; a runner
# container sharing its network namespace; no published ports; both removed at the end.
#
#   interleaved_release_docker.sh <version A> <version B> <output file> <documents> <rounds> [changed] ...
#
# Further "<documents> <rounds> <changed>" triples run one after another on the same
# containers.
set -uo pipefail
A="$1"; B="$2"; OUT="$3"; shift 3
HERE="$(cd "$(dirname "$0")" && pwd)"
M=argon260-il-mongo; R=argon260-il-runner
cleanup() { docker rm -f argon260-il-runner argon260-il-mongo >/dev/null 2>&1; }
trap cleanup EXIT
docker run -d --name "$M" 'mongo:7.0.45@sha256:c53852c00c23ca9f23fc39690350ffa9a80e3642fe8f96879726d8da0abe80a7' mongod --replSet rs0 --bind_ip_all --wiredTigerCacheSizeGB 2 >/dev/null
for _ in $(seq 1 120); do
  docker exec "$M" mongosh --quiet --eval 'try { rs.status() } catch (e) { rs.initiate({_id: "rs0", members: [{_id: 0, host: "localhost:27017"}]}) }; if (!db.hello().isWritablePrimary) quit(1)' >/dev/null 2>&1 && break
  sleep 1
done
# SLOWMS=0 makes mongod log every operation, to see where a command's time goes.
[ -z "${SLOWMS:-}" ] || docker exec "$M" mongosh --quiet --eval "db.setProfilingLevel(0, {slowms: $SLOWMS})" >/dev/null
docker run -d --name "$R" --network "container:$M" node:24-bookworm sleep infinity >/dev/null
docker exec "$R" bash -c 'apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq python3-venv >/dev/null 2>&1; python3 -m venv /root/venv && /root/venv/bin/pip install -q pymongo==4.20.0 2>&1 | tail -1'
for pair in "a:$A" "b:$B"; do
  docker exec "$R" npm install -g --prefix "/opt/${pair%%:*}" "argonctl@${pair#*:}" --allow-scripts=argonctl >/dev/null 2>&1
done
docker cp -q "$HERE/interleaved.py" "$R":/root/interleaved.py
BA=/opt/a/lib/node_modules/argonctl/bin/argon-bin; BB=/opt/b/lib/node_modules/argonctl/bin/argon-bin
{
  echo "A = argonctl@$A, B = argonctl@$B, the executables the npm packages install; MongoDB 7.0.45 one-node replica set, WiredTiger cache 2 GiB"
  docker exec "$R" sha256sum "$BA" "$BB"
} > "$OUT"
status=0
while [ $# -ge 2 ]; do
  N="$1"; ROUNDS="$2"; CHANGED="${3:-100}"; shift 2; [ $# -gt 0 ] && shift
  {
    echo "== $(date -u +%Y-%m-%dT%H:%M:%SZ) $N documents, $ROUNDS rounds, $CHANGED changed; host: $(uptime | sed 's/.*load/load/')"
    docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}'
  } >> "$OUT"
  docker exec -e PYTHONUNBUFFERED=1 -e PAUSE_BEFORE_SECOND_DIFF="${PAUSE_BEFORE_SECOND_DIFF:-0}" "$R" /root/venv/bin/python /root/interleaved.py "$N" "$ROUNDS" "$BA" "$BB" "$CHANGED" >> "$OUT" 2>&1 || status=$?
  echo "== ended $(date -u +%Y-%m-%dT%H:%M:%SZ) exit $status; host: $(uptime | sed 's/.*load/load/')" >> "$OUT"
done
docker logs "$M" > "${OUT%.txt}.mongod.log" 2>&1
exit $status
