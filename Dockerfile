FROM golang:1.26.11-trixie@sha256:cff05dd6b81c901f2e8249eb6f91c69a60451d0f12c26bfef08e476a85b32d4d
RUN apt-get update && apt-get install -y --no-install-recommends python3 git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /suite
COPY . .
# The explicit engine mount is frozen and replaced at run time; no historical
# module version is silently presented as the code under measurement.
ENTRYPOINT ["python3", "scripts/run.py", "--engine", "/engine"]
