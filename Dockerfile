FROM golang:1.24

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /usr/local/bin/argonbench .

ENTRYPOINT ["argonbench"]
CMD ["-out", "/out/report.md"]
