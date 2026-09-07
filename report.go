package main

import (
	"fmt"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type summary struct {
	N   int     `json:"n"`
	Min float64 `json:"min_ms"`
	P50 float64 `json:"p50_ms"`
	P95 float64 `json:"p95_ms"`
	P99 float64 `json:"p99_ms"`
	Max float64 `json:"max_ms"`
}

func summarize(values []float64) summary {
	if len(values) == 0 {
		return summary{}
	}
	v := append([]float64(nil), values...)
	sort.Float64s(v)
	q := func(p float64) float64 { return v[int(math.Ceil(p*float64(len(v))))-1] }
	return summary{len(v), v[0], q(.5), q(.95), q(.99), v[len(v)-1]}
}
func writeFile(path string, data []byte) error {
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}
	return os.WriteFile(path, data, 0644)
}
func markdown(r report) string {
	var b strings.Builder
	fmt.Fprintf(&b, "# Argon workflow benchmark\n\nCompleted %s; duration %.1f seconds. This is an explicitly sourced local diagnostic build, not a released-version claim. Raw samples, build hashes, environment and configuration: `%s`.\n\n", r.FinishedAt.Format("2006-01-02 15:04:05 UTC"), r.FinishedAt.Sub(r.StartedAt).Seconds(), filepath.Base(r.Config.JSON))
	fmt.Fprint(&b, "Percentiles use nearest rank. With fewer than 100 samples, p99 is usually the observed maximum; these are descriptive observations, not a stable tail-latency estimate. All samples, including first execution, are retained. Scenarios run sequentially; workers run closed-loop within a phase.\n\n")
	fmt.Fprint(&b, "Sandbox readiness includes metadata fork, full physical checkout, and acknowledged capture startup. First native query includes a new client connection/handshake and one verified indexed read, after readiness. Capture lag is measured from majority write acknowledgement until a committed WAL record is observed; polling and query latency are included.\n\n")
	fmt.Fprint(&b, "Metadata forks reference inherited history. Checked-out sandboxes materialize full physical copies. dbStats logical data bytes, allocated collection bytes, and allocated index bytes are reported separately. Allocations are quantized and can remain after deletion; before/after differences are observations, not a universal per-branch disk price.\n\n")
	for _, sc := range r.Scenarios {
		fmt.Fprintf(&b, "## %d documents · %d workers · ancestry depth %d\n\nImported head LSN %d; snapshots present immediately after import: %d.\n\n", sc.Documents, sc.Concurrency, sc.AncestryDepth, sc.HeadLSN, sc.AutoSnapshots)
		fmt.Fprint(&b, "| Operation | n | p50 ms | p95 ms | p99 ms | max ms |\n|---|---:|---:|---:|---:|---:|\n")
		ops := make([]string, 0, len(sc.Summaries))
		for op := range sc.Summaries {
			ops = append(ops, op)
		}
		sort.Strings(ops)
		for _, op := range ops {
			s := sc.Summaries[op]
			fmt.Fprintf(&b, "| %s | %d | %.3f | %.3f | %.3f | %.3f |\n", op, s.N, s.P50, s.P95, s.P99, s.Max)
		}
		fmt.Fprint(&b, "\n| Storage observation | Logical data bytes | Allocated collection bytes | Allocated index bytes |\n|---|---:|---:|---:|\n")
		row := func(label string, s dbSize) {
			fmt.Fprintf(&b, "| %s | %d | %d | %d |\n", label, s.LogicalDataBytes, s.AllocatedStorageBytes, s.AllocatedIndexBytes)
		}
		row("metadata before fork samples", sc.Storage.MetadataBefore)
		row("metadata after fork samples", sc.Storage.MetadataAfter)
		row("metadata before divergence", sc.Storage.DivergenceBefore)
		row("metadata after captured divergence", sc.Storage.DivergenceAfter)
		row("metadata after divergent snapshots", sc.Storage.DivergenceSnapshot)
		if len(sc.Storage.CheckoutCopies) > 0 {
			row("one observed checkout (first completed)", sc.Storage.CheckoutCopies[0])
		}
		for i, s := range sc.Storage.DivergentCopies {
			row(fmt.Sprintf("divergent physical copy %d", i), s)
		}
		ratio := float64(0)
		if sc.Storage.ChangedDocumentBSONBytes > 0 {
			ratio = float64(sc.Storage.WALBSONBytes) / float64(sc.Storage.ChangedDocumentBSONBytes)
		}
		fmt.Fprintf(&b, "\nDivergence captured **%d** records: **%d bytes** of stored WAL BSON over **%d bytes** of changed current-document BSON (**%.3f×**). This includes repeated update history and WAL metadata/compressed images. The denominator counts each changed current document once; this ratio excludes snapshots, indexes and physical copies and is not disk amplification.\n\n", sc.Storage.CapturedRecords, sc.Storage.WALBSONBytes, sc.Storage.ChangedDocumentBSONBytes, ratio)
	}
	return b.String()
}
