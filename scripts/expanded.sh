#!/bin/sh
set -eu
: "${ARGON_ENGINE_SOURCE:?Set ARGON_ENGINE_SOURCE to an explicit Argon checkout}"
exec python3 "$(dirname "$0")/run.py" --engine "$ARGON_ENGINE_SOURCE" -- \
  -sizes 1000,50000,1000000 -concurrency 1,4,16 -depths 1,4,16 \
  -metadata-samples 1000 -workflow-samples 200 -read-samples 100 \
  -divergence-docs 1000 -divergence-rounds 10 -timeout 24h "$@"
