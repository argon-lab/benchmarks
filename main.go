// argonbench: reproducible benchmarks for the Argon MongoDB versioning engine.
//
// Every number Argon publishes must come from a run of this suite that anyone
// can reproduce with `docker compose up`. The suite seeds a source database,
// imports it through the argon CLI (creating WAL history), then measures the
// engine's user-visible operations through the same Go API the CLI uses.
//
// Metrics:
//  1. branch creation latency (p50/p95/p99) on a project with real history
//  2. time-travel materialization latency across history depths, as shipped
//  3. effect of a snapshot at head (bounded replay) vs the same read without
//  4. materialization throughput (documents/second)
//  5. storage cost of a branch (bytes added per fork)
//  6. end-to-end import throughput through the CLI (labeled as end-to-end)
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"runtime"
	"runtime/debug"
	"sort"
	"strings"
	"time"

	"github.com/argon-lab/argon/pkg/walcli"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	nDocs     = flag.Int("docs", 50000, "documents to seed and import")
	nIters    = flag.Int("iters", 200, "iterations for branch-create latency")
	nBranches = flag.Int("branches", 200, "branches to create for the storage suite")
	depthsArg = flag.String("depths", "1000,10000,50000", "comma-separated history depths (LSNs) for time-travel")
	outPath   = flag.String("out", "", "also write the markdown report to this path")
)

func main() {
	flag.Parse()
	ctx := context.Background()

	uri := os.Getenv("MONGODB_URI")
	if uri == "" {
		uri = "mongodb://localhost:27017"
	}

	client, err := waitForMongo(ctx, uri, 60*time.Second)
	must(err, "connect to MongoDB")
	defer client.Disconnect(ctx)

	svcs, err := walcli.NewServices()
	must(err, "create argon services")

	var r report
	r.startedAt = time.Now().UTC()
	r.env = collectEnv(ctx, client)

	runID := time.Now().UTC().Format("20060102t150405")
	project := "bench-" + runID
	srcDB := "benchsrc_" + runID

	// ── seed + import (creates the project and its WAL history) ──
	fmt.Fprintf(os.Stderr, "seeding %d documents into %s.items...\n", *nDocs, srcDB)
	must(seedSource(ctx, client, srcDB, *nDocs), "seed source database")

	fmt.Fprintf(os.Stderr, "importing through walcli.ImportDatabase...\n")
	t0 := time.Now()
	_, err = svcs.ImportDatabase(ctx, uri, srcDB, project, false, 1000)
	importDur := time.Since(t0)
	must(err, "import database")
	r.importDocs = *nDocs
	r.importDur = importDur

	proj, err := svcs.Projects.GetProjectByName(project)
	must(err, "fetch imported project")
	main0, err := svcs.Branches.GetBranchByID(proj.MainBranchID)
	must(err, "fetch main branch")
	r.headLSN = main0.HeadLSN

	snaps, err := svcs.Snapshots.ListSnapshots(ctx, main0.ID)
	must(err, "list snapshots")
	r.autoSnapshots = len(snaps)

	// ── 1. branch creation latency ──
	fmt.Fprintf(os.Stderr, "branch creation: %d iterations...\n", *nIters)
	var branchDurs []time.Duration
	for i := 0; i < *nIters; i++ {
		name := fmt.Sprintf("lat-%04d", i)
		t0 := time.Now()
		_, err := svcs.Branches.CreateBranch(proj.ID, name, main0.ID)
		branchDurs = append(branchDurs, time.Since(t0))
		must(err, "create branch")
	}
	r.branchCreate = summarize(branchDurs)

	// ── 2. time-travel latency across depths (as-shipped config) ──
	for _, d := range parseDepths(*depthsArg, main0.HeadLSN) {
		t0 := time.Now()
		state, err := svcs.TimeTravel.MaterializeAtLSN(main0, "items", d)
		dur := time.Since(t0)
		must(err, "time-travel materialize")
		r.timeTravel = append(r.timeTravel, ttResult{lsn: d, docs: len(state), dur: dur})
	}

	// ── 3. snapshot at head: bounded replay vs the same read before ──
	t0 = time.Now()
	pre, err := svcs.TimeTravel.MaterializeAtLSN(main0, "items", main0.HeadLSN)
	r.headBefore = time.Since(t0)
	must(err, "materialize head (before explicit snapshot)")
	r.headDocs = len(pre)

	t0 = time.Now()
	_, err = svcs.Snapshots.CreateSnapshot(ctx, main0.ID, main0.HeadLSN)
	r.snapshotCreate = time.Since(t0)
	must(err, "create snapshot")

	t0 = time.Now()
	_, err = svcs.TimeTravel.MaterializeAtLSN(main0, "items", main0.HeadLSN)
	r.headAfter = time.Since(t0)
	must(err, "materialize head (after snapshot)")

	// ── 4. materialization throughput from the head read ──
	// docs/sec computed in the report from headDocs and headBefore/headAfter.

	// ── 5. storage cost per branch ──
	fmt.Fprintf(os.Stderr, "storage: creating %d branches...\n", *nBranches)
	before, err := dbBytes(ctx, client, "argon_wal")
	must(err, "dbStats before")
	for i := 0; i < *nBranches; i++ {
		_, err := svcs.Branches.CreateBranch(proj.ID, fmt.Sprintf("st-%04d", i), main0.ID)
		must(err, "create storage branch")
	}
	after, err := dbBytes(ctx, client, "argon_wal")
	must(err, "dbStats after")
	r.branchesForStorage = *nBranches
	r.bytesPerBranch = float64(after-before) / float64(*nBranches)

	// ── emit ──
	md := r.markdown()
	fmt.Println(md)
	if *outPath != "" {
		must(os.WriteFile(*outPath, []byte(md), 0o644), "write report")
		fmt.Fprintf(os.Stderr, "report written to %s\n", *outPath)
	}
}

// ── seeding ─────────────────────────────────────────────────────

func seedSource(ctx context.Context, client *mongo.Client, dbName string, n int) error {
	coll := client.Database(dbName).Collection("items")
	const batch = 1000
	docs := make([]interface{}, 0, batch)
	for i := 0; i < n; i++ {
		docs = append(docs, bson.M{
			"_id":   fmt.Sprintf("item-%08d", i),
			"sku":   fmt.Sprintf("SKU-%08d", i),
			"price": float64(i%9000)/100 + 1,
			"qty":   i % 500,
			"tags":  []string{"bench", fmt.Sprintf("cat-%d", i%16)},
			"desc":  strings.Repeat("argon benchmark payload ", 5),
		})
		if len(docs) == batch {
			if _, err := coll.InsertMany(ctx, docs); err != nil {
				return err
			}
			docs = docs[:0]
		}
	}
	if len(docs) > 0 {
		if _, err := coll.InsertMany(ctx, docs); err != nil {
			return err
		}
	}
	return nil
}

// ── helpers ─────────────────────────────────────────────────────

func waitForMongo(ctx context.Context, uri string, timeout time.Duration) (*mongo.Client, error) {
	deadline := time.Now().Add(timeout)
	for {
		client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri))
		if err == nil {
			if err = client.Ping(ctx, nil); err == nil {
				return client, nil
			}
			_ = client.Disconnect(ctx)
		}
		if time.Now().After(deadline) {
			return nil, fmt.Errorf("mongo not reachable within %s: %w", timeout, err)
		}
		time.Sleep(2 * time.Second)
	}
}

func dbBytes(ctx context.Context, client *mongo.Client, db string) (int64, error) {
	var stats struct {
		DataSize  float64 `bson:"dataSize"`
		IndexSize float64 `bson:"indexSize"`
	}
	err := client.Database(db).RunCommand(ctx, bson.D{{Key: "dbStats", Value: 1}}).Decode(&stats)
	return int64(stats.DataSize + stats.IndexSize), err
}

func parseDepths(s string, head int64) []int64 {
	var out []int64
	for _, part := range strings.Split(s, ",") {
		var d int64
		fmt.Sscanf(strings.TrimSpace(part), "%d", &d)
		if d > 0 && d <= head {
			out = append(out, d)
		}
	}
	if len(out) == 0 {
		out = []int64{head}
	}
	return out
}

type latencySummary struct {
	n                  int
	p50, p95, p99, max time.Duration
}

func summarize(durs []time.Duration) latencySummary {
	sorted := append([]time.Duration(nil), durs...)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })
	pick := func(q float64) time.Duration {
		idx := int(q * float64(len(sorted)-1))
		return sorted[idx]
	}
	return latencySummary{
		n: len(sorted), p50: pick(0.50), p95: pick(0.95), p99: pick(0.99),
		max: sorted[len(sorted)-1],
	}
}

func must(err error, what string) {
	if err != nil {
		fmt.Fprintf(os.Stderr, "FATAL: %s: %v\n", what, err)
		os.Exit(1)
	}
}

// ── environment + report ───────────────────────────────────────

type envInfo struct {
	goVersion, goos, goarch string
	numCPU                  int
	mongoVersion            string
	engineRef               string
}

func collectEnv(ctx context.Context, client *mongo.Client) envInfo {
	var build struct {
		Version string `bson:"version"`
	}
	_ = client.Database("admin").RunCommand(ctx, bson.D{{Key: "buildInfo", Value: 1}}).Decode(&build)
	ref := "unknown"
	if bi, ok := debug.ReadBuildInfo(); ok {
		for _, dep := range bi.Deps {
			if dep.Path == "github.com/argon-lab/argon" {
				ref = dep.Version
			}
		}
	}
	return envInfo{
		goVersion: runtime.Version(), goos: runtime.GOOS, goarch: runtime.GOARCH,
		numCPU: runtime.NumCPU(), mongoVersion: build.Version, engineRef: ref,
	}
}

type ttResult struct {
	lsn  int64
	docs int
	dur  time.Duration
}

type report struct {
	startedAt          time.Time
	env                envInfo
	importDocs         int
	importDur          time.Duration
	headLSN            int64
	autoSnapshots      int
	branchCreate       latencySummary
	timeTravel         []ttResult
	headBefore         time.Duration
	headAfter          time.Duration
	headDocs           int
	snapshotCreate     time.Duration
	branchesForStorage int
	bytesPerBranch     float64
}

func ms(d time.Duration) string { return fmt.Sprintf("%.2f ms", float64(d.Microseconds())/1000) }

func (r report) markdown() string {
	var b strings.Builder
	w := func(format string, a ...interface{}) { fmt.Fprintf(&b, format+"\n", a...) }

	w("# argonbench report")
	w("")
	w("| environment | value |")
	w("|---|---|")
	w("| date (UTC) | %s |", r.startedAt.Format("2006-01-02 15:04"))
	w("| engine ref | `%s` |", r.env.engineRef)
	w("| go | %s %s/%s, %d CPUs |", r.env.goVersion, r.env.goos, r.env.goarch, r.env.numCPU)
	w("| mongodb | %s |", r.env.mongoVersion)
	w("| history seeded | %d documents → head LSN %d |", r.importDocs, r.headLSN)
	w("| auto-snapshots after import | %d |", r.autoSnapshots)
	w("")
	w("## 1 · Branch creation latency (n=%d, on a project with %d-entry history)", r.branchCreate.n, r.headLSN)
	w("")
	w("| p50 | p95 | p99 | max |")
	w("|---|---|---|---|")
	w("| %s | %s | %s | %s |", ms(r.branchCreate.p50), ms(r.branchCreate.p95), ms(r.branchCreate.p99), ms(r.branchCreate.max))
	w("")
	w("## 2 · Time-travel materialization (as-shipped configuration)")
	w("")
	w("| target LSN | documents | latency |")
	w("|---|---|---|")
	for _, t := range r.timeTravel {
		w("| %d | %d | %s |", t.lsn, t.docs, ms(t.dur))
	}
	w("")
	w("## 3 · Snapshot at head (bounded replay)")
	w("")
	w("| read at head, before explicit snapshot | snapshot creation | read at head, after |")
	w("|---|---|---|")
	w("| %s | %s | %s |", ms(r.headBefore), ms(r.snapshotCreate), ms(r.headAfter))
	w("")
	w("## 4 · Materialization throughput")
	w("")
	throughput := func(d time.Duration) float64 {
		if d <= 0 {
			return 0
		}
		return float64(r.headDocs) / d.Seconds()
	}
	w("| scenario | documents/second |")
	w("|---|---|")
	w("| before explicit snapshot | %.0f |", throughput(r.headBefore))
	w("| after explicit snapshot | %.0f |", throughput(r.headAfter))
	w("")
	w("## 5 · Storage cost per branch (n=%d)", r.branchesForStorage)
	w("")
	w("| bytes added per branch (data+index) |")
	w("|---|")
	w("| %.0f B |", r.bytesPerBranch)
	w("")
	w("## 6 · Bulk import throughput (walcli.ImportDatabase)")
	w("")
	w("| documents | wall time | docs/second |")
	w("|---|---|---|")
	w("| %d | %.1f s | %.0f |", r.importDocs, r.importDur.Seconds(), float64(r.importDocs)/r.importDur.Seconds())
	w("")
	w("---")
	w("Reproduce: `docker compose up --build` in https://github.com/argon-lab/benchmarks")
	return b.String()
}
