FROM golang:1.24

ARG ENGINE_REF=master
ENV ENGINE_REF=${ENGINE_REF}

# Build the argon CLI from the engine repo at the pinned ref, so the
# seeding path (import) runs exactly the code being measured.
RUN git clone https://github.com/argon-lab/argon /engine \
    && cd /engine && git checkout "${ENGINE_REF}" \
    && cd cli && CGO_ENABLED=0 go build -o /usr/local/bin/argon .

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /usr/local/bin/argonbench .

ENTRYPOINT ["argonbench"]
CMD ["-out", "/out/report.md"]
