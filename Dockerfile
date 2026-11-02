FROM golang:1.26.10-trixie@sha256:909771fef53e3dcb0950255f0c9a8b4728c3b841e61509c7b29b098de7ee02d4
RUN apt-get update && apt-get install -y --no-install-recommends python3 git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /suite
COPY . .
# The explicit engine mount is frozen and replaced at run time; no historical
# module version is silently presented as the code under measurement.
ENTRYPOINT ["python3", "scripts/run.py", "--engine", "/engine"]
