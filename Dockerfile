FROM golang:1.26.6-trixie
RUN apt-get update && apt-get install -y --no-install-recommends python3 git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /suite
COPY . .
# The explicit engine mount is frozen and replaced at run time; no historical
# module version is silently presented as the code under measurement.
ENTRYPOINT ["python3", "scripts/run.py", "--engine", "/engine"]
