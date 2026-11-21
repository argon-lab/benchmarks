#!/usr/bin/env bash
# What a sandbox enforces, run with a published release of Argon: a MongoDB
# user scoped to the sandbox and revoked on discard, and the source's
# secondary indexes built in the sandbox.
#
#   scripts/sandbox_safety_walkthrough_docker.sh <argonctl version> <new output directory>
#
# MongoDB 7.0.45 runs as a one-member replica set with access control
# (--auth --keyFile). The CLI runs in a node container installed from npm.
# Both share one network namespace; nothing is published on the host. Every
# password in the transcript is replaced by •••; the sandbox password is
# printed once by Argon and kept only in this script's memory.
set -euo pipefail
VERSION="${1:?argonctl version, for example 2.11.1}"
OUT="${2:?new output directory}"
[ ! -e "$OUT" ] || { echo "output directory already exists: $OUT" >&2; exit 1; }
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
MONGO_IMAGE='mongo:7.0.45@sha256:c53852c00c23ca9f23fc39690350ffa9a80e3642fe8f96879726d8da0abe80a7'
DB=argonsafety-mongo
CLI=argonsafety-cli
ENGINE_PASSWORD="$(openssl rand -hex 16)"
cleanup() { docker rm -fv "$CLI" "$DB" >/dev/null 2>&1 || true; }
trap cleanup EXIT

T="$OUT/transcript.txt"
: > "$T"
# The CLI logs "WAL Monitor: Started/Stopped health monitoring" on stderr around
# every command; those two lines are left out of the transcript.
mask() { grep -v "WAL Monitor: " | sed -E -e "s#(mongodb://[^:/@]+):[^@]+@#\1:•••@#g" -e "s#$ENGINE_PASSWORD#•••#g"; }
say() { printf '\n## %s\n' "$*" | tee -a "$T"; }
show() { printf '\n$ %s\n' "$*" | tee -a "$T"; }
run() { # run <container> <shown command> <command...>: record a command and its output
  local where=$1 shown=$2; shift 2
  show "$shown"
  docker exec "$where" "$@" 2>&1 | mask | tee -a "$T" || true
}

docker run -d --name "$DB" --entrypoint bash "$MONGO_IMAGE" -ec '
  umask 077; head -c 48 /dev/urandom | base64 > /tmp/key; chown mongodb:mongodb /tmp/key
  exec docker-entrypoint.sh mongod --auth --keyFile /tmp/key --replSet rs0 --bind_ip_all' >/dev/null
for _ in $(seq 1 60); do docker exec "$DB" mongosh --quiet --eval 'db.adminCommand({ping:1})' >/dev/null 2>&1 && break; sleep 1; done
docker exec "$DB" mongosh --quiet --eval 'rs.initiate({_id:"rs0",members:[{_id:0,host:"localhost:27017"}]})' >/dev/null
for _ in $(seq 1 60); do docker exec "$DB" mongosh --quiet --eval 'if (!db.hello().isWritablePrimary) quit(1)' >/dev/null 2>&1 && break; sleep 1; done
docker exec -e P="$ENGINE_PASSWORD" "$DB" mongosh --quiet admin --eval 'db.createUser({user:"argon",pwd:process.env.P,roles:["root"]})' >/dev/null
ENGINE="mongodb://argon:$ENGINE_PASSWORD@localhost:27017/?authSource=admin&replicaSet=rs0"
docker exec "$DB" mongosh --quiet "$ENGINE" --eval '
  const shop = db.getSiblingDB("shop");
  const now = new Date();
  shop.orders.insertMany(Array.from({length: 1000}, (_, i) => ({_id: i, sku: "sku-" + i, status: i % 4 ? "open" : "shipped", total: (i % 50) * 3, createdAt: now})));
  shop.orders.createIndex({sku: 1}, {unique: true});
  shop.orders.createIndex({status: 1, total: -1});
  shop.orders.createIndex({createdAt: 1}, {expireAfterSeconds: 2592000});
  db.getSiblingDB("billing").invoices.insertOne({_id: 1, amount: 120});' >/dev/null

docker run -d --name "$CLI" --network "container:$DB" -e MONGODB_URI="$ENGINE" node:24-bookworm sleep infinity >/dev/null
docker exec "$CLI" npm install -g "argonctl@$VERSION" --allow-scripts=argonctl >/dev/null 2>&1

{
  echo "# What an Argon sandbox enforces"
  echo "argonctl@$VERSION from npm: $(docker exec "$CLI" argon --version)"
  echo "MongoDB $(docker exec "$DB" mongosh --quiet "$ENGINE" --eval 'db.version()') ($MONGO_IMAGE), one-member replica set with --auth --keyFile"
  echo "MONGODB_URI for the CLI is a root user (\$ENGINE). The source database is shop on the same deployment; billing is another database there."
  echo "Started $(date -u +%FT%TZ)"
} | tee -a "$T"

say "The source: shop.orders, 1,000 documents and three secondary indexes"
run "$DB" 'mongosh "$ENGINE" --eval '\''db.getSiblingDB("shop").orders.getIndexes().map(i => i.name)'\''' \
  mongosh --quiet "$ENGINE" --eval 'db.getSiblingDB("shop").orders.getIndexes().map(i => i.name)'

say "Import it (nothing else writes to it)"
run "$CLI" 'argon import database --uri "$ENGINE" --database shop --project shop --source-quiesced --yes' \
  argon import database --uri "$ENGINE" --database shop --project shop --source-quiesced --yes

say "A sandbox with its own MongoDB user"
show 'argon sandbox create -p shop --name agent-run --ttl 1h --credential --output json'
REPLY="$(docker exec "$CLI" argon sandbox create -p shop --name agent-run --ttl 1h --credential --output json 2>/dev/null)"
printf '%s\n' "$REPLY" | mask | tee -a "$T"
URI="$(printf '%s' "$REPLY" | python3 -c 'import json,sys; print(json.load(sys.stdin)["connection_string"])')"
MAIN="$(docker exec "$CLI" argon checkout -p shop -b main --output json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["physical_db"])')"
echo "(\$SANDBOX below is that connection string. main is checked out as $MAIN.)" | tee -a "$T"

say "Inside the sandbox"
run "$DB" 'mongosh "$SANDBOX" --eval '\''db.orders.getIndexes().map(i => i.name + (i.unique ? " unique" : "") + (i.expireAfterSeconds === undefined ? "" : " ttl"))'\''' \
  mongosh --quiet "$URI" --eval 'db.orders.getIndexes().map(i => i.name + (i.unique ? " unique" : "") + (i.expireAfterSeconds === undefined ? "" : " ttl"))'
run "$DB" 'mongosh "$SANDBOX" --eval '\''db.orders.updateOne({_id: 7}, {$set: {status: "refunded"}})'\''' \
  mongosh --quiet "$URI" --eval 'db.orders.updateOne({_id: 7}, {$set: {status: "refunded"}})'
run "$DB" 'mongosh "$SANDBOX" --eval '\''db.orders.insertOne({_id: 5000, sku: "sku-42"})'\''' \
  mongosh --quiet "$URI" --eval 'try { db.orders.insertOne({_id: 5000, sku: "sku-42"}) } catch (e) { print(e.message) }'

say "Outside the sandbox"
run "$DB" 'mongosh "$SANDBOX" --eval '\''db.getSiblingDB("billing").invoices.findOne()'\''' \
  mongosh --quiet "$URI" --eval 'try { printjson(db.getSiblingDB("billing").invoices.findOne()) } catch (e) { print(e.message) }'
run "$DB" "mongosh \"\$SANDBOX\" --eval 'db.getSiblingDB(\"$MAIN\").orders.findOne()'   # main's database" \
  mongosh --quiet "$URI" --eval "try { printjson(db.getSiblingDB('$MAIN').orders.findOne()) } catch (e) { print(e.message) }"
run "$DB" 'mongosh "$SANDBOX" --eval '\''db.getSiblingDB("argon_wal").wal_log.findOne()'\''' \
  mongosh --quiet "$URI" --eval 'try { printjson(db.getSiblingDB("argon_wal").wal_log.findOne()) } catch (e) { print(e.message) }'

say "Discard the sandbox while a connection is still open"
docker exec -d -e U="$URI" "$DB" bash -c 'mongosh --quiet "$U" --eval "
  db.orders.updateOne({_id: 8}, {\$set: {status: \"held\"}}); print(\"first write: ok\");
  sleep(12000);
  try { db.orders.updateOne({_id: 9}, {\$set: {status: \"held\"}}); print(\"second write: ok\") } catch (e) { print(\"second write: \" + e.message) }" > /tmp/open.log 2>&1'
sleep 4
run "$CLI" 'argon sandbox discard -p shop -b agent-run' argon sandbox discard -p shop -b agent-run
sleep 12
show '# output of the connection opened before the discard'
docker exec "$DB" cat /tmp/open.log | mask | tee -a "$T"
run "$DB" 'mongosh "$SANDBOX" --eval '\''db.orders.findOne()'\''   # a new connection' \
  mongosh --quiet "$URI" --eval 'db.orders.findOne()'

say "An index the data violates"
run "$CLI" 'argon branches create cleanup -p shop --from main' argon branches create cleanup -p shop --from main
show 'argon checkout -p shop -b cleanup'
CLEAN="$(docker exec "$CLI" argon checkout -p shop -b cleanup --output json 2>/dev/null)"
printf '%s\n' "$CLEAN" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("checked out as", d["physical_db"], "with", d["indexes"], "secondary index(es)")' | tee -a "$T"
CLEAN_URI="$(printf '%s' "$CLEAN" | python3 -c 'import json,sys; print(json.load(sys.stdin)["connection_string"])')"
docker exec -d "$CLI" bash -c 'argon watch -p shop -b cleanup > /tmp/watch.log 2>&1'
sleep 3
show 'argon watch -p shop -b cleanup &   # capture the branch'"'"'s writes'
run "$DB" 'mongosh "$CLEANUP" --eval '\''db.orders.dropIndex("sku_1"); db.orders.insertOne({_id: 6000, sku: "sku-42"})'\''' \
  mongosh --quiet "$CLEAN_URI" --eval 'db.orders.dropIndex("sku_1"); printjson(db.orders.insertOne({_id: 6000, sku: "sku-42"}))'
sleep 3
show 'argon merge preview -p shop -b cleanup'
PREVIEW="$(docker exec "$CLI" argon merge preview -p shop -b cleanup 2>&1)"
printf '%s\n' "$PREVIEW" | mask | tee -a "$T"
PLAN="$(printf '%s' "$PREVIEW" | grep -oE 'Plan [0-9a-f]{24} saved' | awk '{print $2}')"
run "$CLI" "argon merge apply $PLAN   # main is checked out and has sku_1" argon merge apply "$PLAN"
run "$CLI" 'argon branches list -p shop' argon branches list -p shop
say "The same merge with main not checked out"
run "$CLI" 'argon release -p shop -b main' argon release -p shop -b main
run "$CLI" "argon merge apply $PLAN" argon merge apply "$PLAN"
show 'argon merge preview -p shop -b cleanup'
PREVIEW="$(docker exec "$CLI" argon merge preview -p shop -b cleanup 2>&1)"
printf '%s\n' "$PREVIEW" | mask | tee -a "$T"
PLAN="$(printf '%s' "$PREVIEW" | grep -oE 'Plan [0-9a-f]{24} saved' | awk '{print $2}')"
run "$CLI" "argon merge apply $PLAN" argon merge apply "$PLAN"
run "$CLI" 'argon sandbox create -p shop --name next-run --ttl 1h' argon sandbox create -p shop --name next-run --ttl 1h

echo | tee -a "$T"
echo "Finished $(date -u +%FT%TZ)" | tee -a "$T"
docker logs "$DB" > "$OUT/mongod.log" 2>&1 || true
gzip -9 "$OUT/mongod.log"
if grep -q "$ENGINE_PASSWORD" "$T"; then echo "engine password leaked into the transcript" >&2; exit 1; fi
if grep -qE 'mongodb://sandbox_[^:]+:[^•@]+@' "$T"; then echo "sandbox password leaked into the transcript" >&2; exit 1; fi
echo "wrote $T"
