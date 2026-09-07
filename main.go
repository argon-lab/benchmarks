// argonbench measures observable workflows against an explicit engine source snapshot.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/argon-lab/argon/pkg/walcli"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type config struct {
	Sizes            string        `json:"sizes"`
	Concurrency      string        `json:"concurrency"`
	Depths           string        `json:"ancestry_depths"`
	MetadataSamples  int           `json:"metadata_samples"`
	WorkflowSamples  int           `json:"workflow_samples"`
	ReadSamples      int           `json:"read_samples"`
	DivergenceDocs   int           `json:"divergence_docs_per_branch"`
	DivergenceRounds int           `json:"divergence_rounds"`
	CapturePollMS    int           `json:"capture_poll_ms"`
	Timeout          time.Duration `json:"timeout_ns"`
	Out              string        `json:"report_path"`
	JSON             string        `json:"raw_path"`
	Provenance       string        `json:"provenance_path"`
}
type sample struct {
	Operation string  `json:"operation"`
	Iteration int     `json:"iteration"`
	MS        float64 `json:"ms"`
}
type dbSize struct {
	LogicalDataBytes      int64 `json:"logical_data_bytes"`
	AllocatedStorageBytes int64 `json:"allocated_storage_bytes"`
	AllocatedIndexBytes   int64 `json:"allocated_index_bytes"`
}
type storageResult struct {
	MetadataBefore           dbSize   `json:"metadata_before_forks"`
	MetadataAfter            dbSize   `json:"metadata_after_forks"`
	CheckoutCopies           []dbSize `json:"checkout_copies"`
	DivergenceBefore         dbSize   `json:"metadata_before_divergence"`
	DivergenceAfter          dbSize   `json:"metadata_after_capture"`
	DivergenceSnapshot       dbSize   `json:"metadata_after_divergence_snapshots"`
	DivergentCopies          []dbSize `json:"divergent_physical_copies"`
	CapturedRecords          int64    `json:"captured_records"`
	WALBSONBytes             int64    `json:"wal_bson_bytes"`
	ChangedDocumentBSONBytes int64    `json:"changed_document_bson_bytes"`
}
type scenario struct {
	Documents     int                `json:"documents"`
	Concurrency   int                `json:"concurrency"`
	AncestryDepth int                `json:"ancestry_depth"`
	HeadLSN       int64              `json:"import_head_lsn"`
	AutoSnapshots int                `json:"snapshots_after_import"`
	Samples       []sample           `json:"samples"`
	Summaries     map[string]summary `json:"summaries"`
	Storage       storageResult      `json:"storage"`
}
type report struct {
	SchemaVersion int                    `json:"schema_version"`
	StartedAt     time.Time              `json:"started_at"`
	FinishedAt    time.Time              `json:"finished_at"`
	Config        config                 `json:"config"`
	Provenance    json.RawMessage        `json:"provenance"`
	Environment   map[string]interface{} `json:"environment"`
	Scenarios     []scenario             `json:"scenarios"`
	Complete      bool                   `json:"complete"`
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "benchmark failed:", err)
		os.Exit(1)
	}
}
func run() error {
	c := config{}
	flag.StringVar(&c.Sizes, "sizes", "1000,10000", "comma-separated imported document counts")
	flag.StringVar(&c.Concurrency, "concurrency", "1,4", "closed-loop workers per scenario")
	flag.StringVar(&c.Depths, "depths", "1,4", "ancestry edges between imported main and workload parent")
	flag.IntVar(&c.MetadataSamples, "metadata-samples", 100, "total metadata fork samples per scenario")
	flag.IntVar(&c.WorkflowSamples, "workflow-samples", 20, "total sandbox/capture workflow samples per scenario")
	flag.IntVar(&c.ReadSamples, "read-samples", 20, "samples per materialization phase")
	flag.IntVar(&c.DivergenceDocs, "divergence-docs", 100, "distinct documents updated per divergent branch, capped at size")
	flag.IntVar(&c.DivergenceRounds, "divergence-rounds", 3, "update rounds per divergent branch")
	flag.IntVar(&c.CapturePollMS, "capture-poll-ms", 2, "WAL visibility polling interval, included in observed lag")
	flag.DurationVar(&c.Timeout, "timeout", 30*time.Minute, "whole-run deadline")
	flag.StringVar(&c.Out, "out", "results/report.md", "Markdown report destination")
	flag.StringVar(&c.JSON, "json", "results/raw.json", "raw JSON destination")
	flag.StringVar(&c.Provenance, "provenance", "", "required JSON produced by scripts/run.py")
	flag.Parse()
	sizes, err := positiveList(c.Sizes)
	if err != nil {
		return err
	}
	conc, err := positiveList(c.Concurrency)
	if err != nil {
		return err
	}
	depths, err := positiveList(c.Depths)
	if err != nil {
		return err
	}
	if c.MetadataSamples < 1 || c.WorkflowSamples < 1 || c.ReadSamples < 1 || c.DivergenceDocs < 1 || c.DivergenceRounds < 1 || c.CapturePollMS < 1 {
		return fmt.Errorf("sample counts, rounds and poll interval must be positive")
	}
	if c.Provenance == "" {
		return fmt.Errorf("use scripts/run.py with an explicit engine checkout to capture build provenance")
	}
	prov, err := os.ReadFile(c.Provenance)
	if err != nil {
		return err
	}
	if !json.Valid(prov) {
		return fmt.Errorf("invalid provenance JSON")
	}
	uri := os.Getenv("MONGODB_URI")
	if uri == "" {
		uri = "mongodb://localhost:27017/?replicaSet=rs0"
	}
	ctx, cancel := context.WithTimeout(context.Background(), c.Timeout)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(uri).SetServerSelectionTimeout(10*time.Second))
	if err != nil {
		return err
	}
	defer client.Disconnect(context.Background())
	if err = client.Ping(ctx, nil); err != nil {
		return err
	}
	var hello bson.M
	if err = client.Database("admin").RunCommand(ctx, bson.D{{Key: "hello", Value: 1}}).Decode(&hello); err != nil {
		return err
	}
	if hello["setName"] == nil {
		return fmt.Errorf("MongoDB replica set required for capture and transactions")
	}
	env := map[string]interface{}{"go": runtime.Version(), "os": runtime.GOOS, "arch": runtime.GOARCH, "logical_cpus": runtime.NumCPU(), "gomaxprocs": runtime.GOMAXPROCS(0), "replica_set": hello["setName"], "write_concern": "native measured writes: majority; engine transaction commits: majority", "chunk_store": "mongodb", "timing": "monotonic wall clock; no warmup discarded; closed-loop concurrency"}
	var build bson.M
	_ = client.Database("admin").RunCommand(ctx, bson.D{{Key: "buildInfo", Value: 1}}).Decode(&build)
	env["mongodb_version"] = build["version"]
	var status bson.M
	if e := client.Database("admin").RunCommand(ctx, bson.D{{Key: "serverStatus", Value: 1}}).Decode(&status); e == nil {
		env["mongodb_storage_engine"] = status["storageEngine"]
	}
	var repl bson.M
	if e := client.Database("admin").RunCommand(ctx, bson.D{{Key: "replSetGetConfig", Value: 1}}).Decode(&repl); e == nil {
		if config, ok := repl["config"].(bson.M); ok {
			env["replica_member_count"] = len(config["members"].(bson.A))
			env["majority_journal_default"] = config["writeConcernMajorityJournalDefault"]
		}
	}
	env["isolation"] = "shared developer host; background system load is not controlled"

	for _, key := range []string{"machdep.cpu.brand_string", "hw.memsize", "kern.osproductversion"} {
		if data, e := exec.Command("sysctl", "-n", key).Output(); e == nil {
			env[key] = strings.TrimSpace(string(data))
		}
	}
	if store := os.Getenv("ARGON_SNAPSHOT_STORE"); store != "" && store != "mongodb" {
		return fmt.Errorf("storage suite requires MongoDB chunk storage, unset ARGON_SNAPSHOT_STORE")
	}
	r := report{SchemaVersion: 2, StartedAt: time.Now().UTC(), Config: c, Provenance: prov, Environment: env}
	for _, n := range sizes {
		for _, workers := range conc {
			for _, depth := range depths {
				fmt.Fprintf(os.Stderr, "scenario docs=%d workers=%d ancestry=%d\n", n, workers, depth)
				sc, e := runScenario(ctx, uri, client, c, n, workers, depth)
				if e != nil {
					return fmt.Errorf("docs=%d workers=%d ancestry=%d: %w", n, workers, depth, e)
				}
				r.Scenarios = append(r.Scenarios, sc)
			}
		}
	}
	r.FinishedAt = time.Now().UTC()
	r.Complete = true
	raw, err := json.MarshalIndent(r, "", "  ")
	if err != nil {
		return err
	}
	if err = writeFile(c.JSON, append(raw, '\n')); err != nil {
		return err
	}
	return writeFile(c.Out, []byte(markdown(r)))
}

func positiveList(s string) ([]int, error) {
	out := []int{}
	for _, p := range strings.Split(s, ",") {
		n, e := strconv.Atoi(strings.TrimSpace(p))
		if e != nil || n < 1 {
			return nil, fmt.Errorf("invalid positive integer list %q", s)
		}
		out = append(out, n)
	}
	return out, nil
}
func measure(fn func() error) (float64, error) {
	start := time.Now()
	err := fn()
	return float64(time.Since(start)) / float64(time.Millisecond), err
}
func parallel(ctx context.Context, n, workers int, fn func(int) error) error {
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()
	jobs := make(chan int)
	var wg sync.WaitGroup
	var once sync.Once
	var first error
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := range jobs {
				if ctx.Err() != nil {
					return
				}
				if err := fn(i); err != nil {
					once.Do(func() { first = err; cancel() })
					return
				}
			}
		}()
	}
send:
	for i := 0; i < n; i++ {
		select {
		case jobs <- i:
		case <-ctx.Done():
			break send
		}
	}
	close(jobs)
	wg.Wait()
	if first != nil {
		return first
	}
	return ctx.Err()
}
func statsDB(ctx context.Context, c *mongo.Client, name string) (dbSize, error) {
	var v struct {
		Data    float64 `bson:"dataSize"`
		Storage float64 `bson:"storageSize"`
		Index   float64 `bson:"indexSize"`
	}
	e := c.Database(name).RunCommand(ctx, bson.D{{Key: "dbStats", Value: 1}, {Key: "scale", Value: 1}}).Decode(&v)
	return dbSize{int64(v.Data), int64(v.Storage), int64(v.Index)}, e
}
func seed(ctx context.Context, c *mongo.Client, db string, n int) error {
	for start := 0; start < n; start += 1000 {
		docs := []interface{}{}
		for i := start; i < n && i < start+1000; i++ {
			docs = append(docs, bson.M{"_id": fmt.Sprintf("item-%08d", i), "name": fmt.Sprintf("Item %d", i), "qty": int32(0), "price": float64(i%10000) / 100, "category": fmt.Sprintf("cat-%d", i%20), "payload": strings.Repeat("x", 128)})
		}
		if _, e := c.Database(db).Collection("items").InsertMany(ctx, docs); e != nil {
			return e
		}
	}
	return nil
}

func runScenario(ctx context.Context, uri string, client *mongo.Client, c config, n, workers, depth int) (sc scenario, err error) {
	sc = scenario{Documents: n, Concurrency: workers, AncestryDepth: depth, Summaries: map[string]summary{}}
	suffix := primitive.NewObjectID().Hex()
	meta := "argonbench_meta_" + suffix
	source := "argonbench_src_" + suffix
	project := "bench-" + suffix
	svcs, err := walcli.NewServicesAt(uri, meta)
	if err != nil {
		return sc, err
	}
	var mu sync.Mutex
	physical := map[string]bool{}
	active := map[string]bool{}
	remember := func(branch, db string) { mu.Lock(); active[branch] = true; physical[db] = true; mu.Unlock() }
	add := func(op string, i int, ms float64) {
		mu.Lock()
		sc.Samples = append(sc.Samples, sample{op, i, ms})
		mu.Unlock()
	}
	defer func() {
		clean, cancel := context.WithTimeout(context.Background(), 60*time.Second)
		defer cancel()
		for id := range active {
			_ = svcs.Ingest.Stop(clean, id)
		}

		if waitErr := svcs.WaitAuto(clean); waitErr != nil && err == nil {
			err = fmt.Errorf("snapshot fixture cleanup: %w", waitErr)
		}
		svcs.Monitor.Stop()
		for db := range physical {
			_ = client.Database(db).Drop(clean)
		}
		_ = client.Database(source).Drop(clean)
		_ = client.Database(meta).Drop(clean)
		_ = svcs.Client.Disconnect(clean)
	}()
	if err = seed(ctx, client, source, n); err != nil {
		return sc, err
	}
	ms, err := measure(func() error { _, e := svcs.ImportDatabase(ctx, uri, source, project, false, 1000); return e })
	if err != nil {
		return sc, err
	}
	add("import_ms", 0, ms)
	proj, err := svcs.Projects.GetProjectByName(project)
	if err != nil {
		return sc, err
	}
	parent, err := svcs.Branches.GetBranchByID(proj.MainBranchID)
	if err != nil {
		return sc, err
	}
	mainBranch := parent
	sc.HeadLSN = parent.HeadLSN
	snaps, err := svcs.Snapshots.ListSnapshots(ctx, parent.ID)
	if err != nil {
		return sc, err
	}
	sc.AutoSnapshots = len(snaps)
	for i := 0; i < depth; i++ {
		parent, err = svcs.Branches.CreateBranch(proj.ID, fmt.Sprintf("ancestor-%d", i), parent.ID)
		if err != nil {
			return sc, err
		}
	}
	sc.Storage.MetadataBefore, err = statsDB(ctx, client, meta)
	if err != nil {
		return sc, err
	}
	err = parallel(ctx, c.MetadataSamples, workers, func(i int) error {
		ms, e := measure(func() error {
			_, e := svcs.Branches.CreateBranch(proj.ID, fmt.Sprintf("metadata-%d", i), parent.ID)
			return e
		})
		if e == nil {
			add("metadata_fork_ms", i, ms)
		}
		return e
	})
	if err != nil {
		return sc, err
	}
	sc.Storage.MetadataAfter, err = statsDB(ctx, client, meta)
	if err != nil {
		return sc, err
	}
	read := func(label string) error {
		return parallel(ctx, c.ReadSamples, workers, func(i int) error {
			ms, e := measure(func() error {
				state, e := svcs.Materializer.MaterializeCollection(parent, "items")
				if e == nil && len(state) != n {
					return fmt.Errorf("materialized %d docs, want %d", len(state), n)
				}
				return e
			})
			if e == nil {
				add(label, i, ms)
			}
			return e
		})
	}
	if err = read("head_materialize_as_shipped_ms"); err != nil {
		return sc, err
	}
	ms, err = measure(func() error { _, e := svcs.Snapshots.CreateSnapshot(ctx, mainBranch.ID, mainBranch.HeadLSN); return e })
	if err != nil {
		return sc, err
	}
	add("explicit_snapshot_ms", 0, ms)
	if err = read("head_materialize_after_snapshot_ms"); err != nil {
		return sc, err
	}
	for _, pct := range []int64{25, 50} {
		lsn := int64(n) * pct / 100
		if lsn < 1 {
			lsn = 1
		}
		err = parallel(ctx, c.ReadSamples, workers, func(i int) error {
			ms, e := measure(func() error {
				state, e := svcs.TimeTravel.MaterializeAtLSN(parent, "items", lsn)
				if e == nil && len(state) == 0 {
					return fmt.Errorf("empty historical materialization at LSN %d", lsn)
				}
				return e
			})
			if e == nil {
				add(fmt.Sprintf("historical_%dpct_ms", pct), i, ms)
			}
			return e
		})
		if err != nil {
			return sc, err
		}
	}
	err = parallel(ctx, c.WorkflowSamples, workers, func(i int) error {
		return workflow(ctx, uri, client, svcs, meta, proj.ID, parent.ID, c, i, add, remember, func(s dbSize) {
			mu.Lock()
			sc.Storage.CheckoutCopies = append(sc.Storage.CheckoutCopies, s)
			mu.Unlock()
		})
	})
	if err != nil {
		return sc, err
	}
	err = divergence(ctx, uri, client, svcs, meta, proj.ID, parent.ID, c, n, workers, &sc, add, remember)
	if err != nil {
		return sc, err
	}
	byOp := map[string][]float64{}
	for _, s := range sc.Samples {
		byOp[s.Operation] = append(byOp[s.Operation], s.MS)
	}
	for op, values := range byOp {
		sc.Summaries[op] = summarize(values)
	}
	return sc, nil
}
