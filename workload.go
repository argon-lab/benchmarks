package main

import (
	"context"
	"fmt"
	"time"

	"github.com/argon-lab/argon/pkg/walcli"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/writeconcern"
)

func workflow(ctx context.Context, uri string, client *mongo.Client, s *walcli.Services, meta, project, parent string, c config, i int, add func(string, int, float64), remember func(string, string), copySize func(dbSize)) error {
	start := time.Now()
	sb, err := s.Sandbox.Create(ctx, project, parent, fmt.Sprintf("workflow-%d", i), time.Hour)
	if err != nil {
		return err
	}
	remember(sb.BranchID, sb.PhysicalDB)
	if err = s.StartCapture(ctx, sb.BranchID, "benchmark"); err != nil {
		return err
	}
	add("sandbox_capture_ready_ms", i, float64(time.Since(start))/float64(time.Millisecond))
	start = time.Now()
	native, err := mongo.Connect(ctx, options.Client().ApplyURI(uri).SetWriteConcern(writeconcern.Majority()))
	if err != nil {
		return err
	}
	defer native.Disconnect(context.Background())
	var first bson.M
	if err = native.Database(sb.PhysicalDB).Collection("items").FindOne(ctx, bson.M{"_id": "item-00000000"}).Decode(&first); err != nil {
		return err
	}
	add("first_native_query_ms", i, float64(time.Since(start))/float64(time.Millisecond))
	size, err := statsDB(ctx, client, sb.PhysicalDB)
	if err != nil {
		return err
	}
	copySize(size)
	before, err := s.Branches.GetBranchByID(sb.BranchID)
	if err != nil {
		return err
	}
	start = time.Now()
	result, err := native.Database(sb.PhysicalDB).Collection("items").UpdateOne(ctx, bson.M{"_id": "item-00000000"}, bson.M{"$inc": bson.M{"qty": 1}})
	if err != nil {
		return err
	}
	if result.ModifiedCount != 1 {
		return fmt.Errorf("native update modified %d documents", result.ModifiedCount)
	}
	acked := time.Now()
	add("native_write_ack_ms", i, float64(acked.Sub(start))/float64(time.Millisecond))
	deadline, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	ticker := time.NewTicker(time.Duration(c.CapturePollMS) * time.Millisecond)
	defer ticker.Stop()
	for {
		err = client.Database(meta).Collection("wal_log").FindOne(deadline, bson.M{"branch_id": sb.BranchID, "collection": "items", "document_id": "item-00000000", "lsn": bson.M{"$gt": before.HeadLSN}}).Err()
		if err == nil {
			break
		}
		if err != mongo.ErrNoDocuments {
			return err
		}
		select {
		case <-deadline.Done():
			return fmt.Errorf("capture visibility: %w", deadline.Err())
		case <-ticker.C:
		}
	}
	observed := time.Now()
	add("capture_ack_to_observed_ms", i, float64(observed.Sub(acked))/float64(time.Millisecond))
	add("native_write_to_observed_ms", i, float64(observed.Sub(start))/float64(time.Millisecond))
	if err = s.SyncBranch(ctx, sb.BranchID); err != nil {
		return err
	}
	branch, err := s.Branches.GetBranchByID(sb.BranchID)
	if err != nil {
		return err
	}
	doc, err := s.Materializer.MaterializeDocument(branch, "items", "item-00000000")
	if err != nil {
		return err
	}
	if !qtyEquals(doc["qty"], 1) {
		return fmt.Errorf("captured materialization qty=%v, want 1", doc["qty"])
	}
	return s.Sandbox.Discard(ctx, sb.BranchID)
}
func qtyEquals(v interface{}, n int) bool {
	switch x := v.(type) {
	case int32:
		return int(x) == n
	case int64:
		return int(x) == n
	case int:
		return x == n
	case float64:
		return x == float64(n)
	}
	return false
}

func divergence(ctx context.Context, uri string, client *mongo.Client, s *walcli.Services, meta, project, parent string, c config, n, workers int, sc *scenario, add func(string, int, float64), remember func(string, string)) error {
	ids := make([]string, workers)
	dbs := make([]string, workers)
	for w := 0; w < workers; w++ {
		sb, err := s.Sandbox.Create(ctx, project, parent, fmt.Sprintf("divergence-%d", w), time.Hour)
		if err != nil {
			return err
		}
		remember(sb.BranchID, sb.PhysicalDB)
		ids[w] = sb.BranchID
		dbs[w] = sb.PhysicalDB
		if err = s.StartCapture(ctx, sb.BranchID, "benchmark"); err != nil {
			return err
		}
	}
	var err error
	sc.Storage.DivergenceBefore, err = statsDB(ctx, client, meta)
	if err != nil {
		return err
	}
	docs := c.DivergenceDocs
	if docs > n {
		docs = n
	}
	native, err := mongo.Connect(ctx, options.Client().ApplyURI(uri).SetWriteConcern(writeconcern.Majority()))
	if err != nil {
		return err
	}
	defer native.Disconnect(context.Background())
	err = parallel(ctx, workers, workers, func(w int) error {
		ms, e := measure(func() error {
			for r := 0; r < c.DivergenceRounds; r++ {
				models := make([]mongo.WriteModel, 0, docs)
				for i := 0; i < docs; i++ {
					models = append(models, mongo.NewUpdateOneModel().SetFilter(bson.M{"_id": fmt.Sprintf("item-%08d", i)}).SetUpdate(bson.M{"$inc": bson.M{"qty": 1}}))
				}
				res, e := native.Database(dbs[w]).Collection("items").BulkWrite(ctx, models)
				if e != nil {
					return e
				}
				if res.ModifiedCount != int64(docs) {
					return fmt.Errorf("divergence modified %d, want %d", res.ModifiedCount, docs)
				}
			}
			return s.SyncBranch(ctx, ids[w])
		})
		if e == nil {
			add("divergence_bulk_and_capture_ms", w, ms)
		}
		return e
	})
	if err != nil {
		return err
	}
	sc.Storage.DivergenceAfter, err = statsDB(ctx, client, meta)
	if err != nil {
		return err
	}
	pipeline := mongo.Pipeline{bson.D{{Key: "$match", Value: bson.M{"branch_id": bson.M{"$in": ids}, "collection": "items"}}}, bson.D{{Key: "$group", Value: bson.M{"_id": nil, "count": bson.M{"$sum": 1}, "bytes": bson.M{"$sum": bson.M{"$bsonSize": "$$ROOT"}}}}}}
	cur, err := client.Database(meta).Collection("wal_log").Aggregate(ctx, pipeline)
	if err != nil {
		return err
	}
	defer cur.Close(ctx)
	var aggregate []struct {
		Count int64 `bson:"count"`
		Bytes int64 `bson:"bytes"`
	}
	if err = cur.All(ctx, &aggregate); err != nil {
		return err
	}
	if len(aggregate) != 1 {
		return fmt.Errorf("no captured divergence records")
	}
	sc.Storage.CapturedRecords = aggregate[0].Count
	sc.Storage.WALBSONBytes = aggregate[0].Bytes
	expected := int64(workers * docs * c.DivergenceRounds)
	if sc.Storage.CapturedRecords != expected {
		return fmt.Errorf("capture count %d, want %d", sc.Storage.CapturedRecords, expected)
	}
	for w, id := range ids {
		branch, e := s.Branches.GetBranchByID(id)
		if e != nil {
			return e
		}
		doc, e := s.Materializer.MaterializeDocument(branch, "items", "item-00000000")
		if e != nil {
			return e
		}
		if !qtyEquals(doc["qty"], c.DivergenceRounds) {
			return fmt.Errorf("diverged materialization qty=%v, want %d", doc["qty"], c.DivergenceRounds)
		}
		for i := 0; i < docs; i++ {
			raw, e := native.Database(dbs[w]).Collection("items").FindOne(ctx, bson.M{"_id": fmt.Sprintf("item-%08d", i)}).Raw()
			if e != nil {
				return e
			}
			sc.Storage.ChangedDocumentBSONBytes += int64(len(raw))
		}
		ms, e := measure(func() error { _, e := s.Snapshots.CreateSnapshot(ctx, id, branch.HeadLSN); return e })
		if e != nil {
			return e
		}
		add("divergence_snapshot_ms", w, ms)
		size, e := statsDB(ctx, client, dbs[w])
		if e != nil {
			return e
		}
		sc.Storage.DivergentCopies = append(sc.Storage.DivergentCopies, size)
	}
	sc.Storage.DivergenceSnapshot, err = statsDB(ctx, client, meta)
	return err
}
