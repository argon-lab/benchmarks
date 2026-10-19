FROM golang:1.26.9-trixie@sha256:f06b7122f888680048afb247c4e5f49c0069eb6c4c1ccae0f3f4834527a8d22c
RUN apt-get update && apt-get install -y --no-install-recommends python3 git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /suite
COPY . .
# The explicit engine mount is frozen and replaced at run time; no historical
# module version is silently presented as the code under measurement.
ENTRYPOINT ["python3", "scripts/run.py", "--engine", "/engine"]
