#!/usr/bin/env bash
# Run live_source_walkthrough.py with a MongoDB Atlas cluster as the source.
# Argon's own MongoDB (metadata and sandboxes) is a 7.0.45 one-member replica
# set in a container; the runner installs argonctl from npm. Nothing is
# published on the host. The Atlas connection string is read from a file and
# never printed: the transcript masks the cluster's host and replica-set IDs,
# and the script fails if the password or the full host appears in any output.
#
#   atlas_source_walkthrough_docker.sh <argonctl version> <new output directory> <file with the Atlas URI> [ORDERS]
#
# The Atlas user needs read and write on the database "shop", which the run
# creates and drops (CLEAN_SOURCE=1).
set -uo pipefail
VERSION="${1:?argonctl version, for example 2.12.0}"
OUT="${2:?new output directory}"
URI_FILE="${3:?file holding the mongodb+srv:// connection string}"
ORDERS="${4:-2000}"
[ ! -e "$OUT" ] || { echo "output directory already exists: $OUT" >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
ATLAS_URI="$(cat "$URI_FILE")"
HOST="$(printf '%s' "$ATLAS_URI" | sed -E 's#^mongodb\+srv://[^@]*@([^/?]+).*#\1#')"
PASS="$(printf '%s' "$ATLAS_URI" | sed -E 's#^mongodb\+srv://[^:]*:([^@]*)@.*#\1#')"
NET=argon-atlaspost-net
cleanup() { docker rm -fv argon-atlaspost-runner argon-atlaspost-meta >/dev/null 2>&1; docker network rm "$NET" >/dev/null 2>&1; }
trap cleanup EXIT
cleanup
docker network create "$NET" >/dev/null
IMAGE='mongo:7.0.45@sha256:c53852c00c23ca9f23fc39690350ffa9a80e3642fe8f96879726d8da0abe80a7'
docker run -d --name argon-atlaspost-meta --network "$NET" "$IMAGE" mongod --replSet rs0 --bind_ip_all >/dev/null
for _ in $(seq 1 120); do
  docker exec argon-atlaspost-meta mongosh --quiet --eval "try { rs.status() } catch (e) { rs.initiate({_id: 'rs0', members: [{_id: 0, host: 'argon-atlaspost-meta:27017'}]}) }; if (!db.hello().isWritablePrimary) quit(1)" >/dev/null 2>&1 && break
  sleep 1
done
docker run -d --name argon-atlaspost-runner --network "$NET" -v "$OUT":/out node:24-bookworm sleep infinity >/dev/null
docker exec argon-atlaspost-runner bash -c 'apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq python3-venv >/dev/null 2>&1; python3 -m venv /root/venv && /root/venv/bin/pip install -q pymongo==4.20.0 2>&1 | tail -1'
docker exec argon-atlaspost-runner npm install -g "argonctl@$VERSION" --allow-scripts=argonctl >/dev/null 2>&1
docker cp -q "$HERE/live_source_walkthrough.py" argon-atlaspost-runner:/root/live_source_walkthrough.py
# The npm launcher (bin/argon.js) does not pass signals on to the binary, so
# a follower stopped with SIGINT through it keeps running. Call the binary.
docker exec -e PYTHONUNBUFFERED=1 -e ORDERS="$ORDERS" -e CLEAN_SOURCE=1 \
  -e ARGON=/usr/local/lib/node_modules/argonctl/bin/argon-bin \
  -e WRITE_INTERVAL_SECONDS="${WRITE_INTERVAL_SECONDS:-0.05}" \
  -e SOURCE_URI="$ATLAS_URI" \
  -e MONGODB_URI='mongodb://argon-atlaspost-meta:27017/?replicaSet=rs0' \
  argon-atlaspost-runner /root/venv/bin/python /root/live_source_walkthrough.py > "$OUT/transcript.raw" 2>&1
status=$?
docker exec argon-atlaspost-runner sha256sum /usr/local/lib/node_modules/argonctl/bin/argon-bin > "$OUT/binary-sha256.txt" 2>&1
# Mask the cluster: its SRV host, member hosts and replica-set names carry the
# cluster's ID. The masked forms keep the shape so the reader can follow.
mask() {
  sed -E -e "s#mongodb\+srv://[^@/ ]*@#mongodb+srv://•••@#g" \
         -e 's#([a-z0-9-]+)\.[a-z0-9]{5,}\.mongodb\.net#\1.<id>.mongodb.net#g' \
         -e 's#atlas-[a-z0-9]+-shard#atlas-<id>-shard#g'
}
mask < "$OUT/transcript.raw" > "$OUT/transcript.txt" && rm -f "$OUT/transcript.raw"
if [ -f "$OUT/follow.log" ]; then mask < "$OUT/follow.log" > "$OUT/follow.tmp" && mv "$OUT/follow.tmp" "$OUT/follow.log"; fi
leak=0
for f in "$OUT"/*; do
  { grep -qF -- "$PASS" "$f" || grep -qF -- "$HOST" "$f"; } && { echo "the Atlas password or host appears in $f" >&2; leak=1; }
done
[ $leak -eq 0 ] || exit 1
echo "wrote $OUT/transcript.txt (exit $status)"
exit $status
