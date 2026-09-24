package main

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestReleaseProvenanceLabel(t *testing.T) {
	for _, tc := range []struct {
		provenance string
		released   bool
	}{
		{`{"engine":{"release_tag":"v2.1.2","git_head":"abc","dirty":false}}`, true},
		{`{"engine":{"release_tag":"v2.1.2","git_head":"abc","dirty":true}}`, false},
		{`{"engine":{"git_head":"abc","dirty":false}}`, false},
	} {
		got := markdown(report{Provenance: json.RawMessage(tc.provenance)})
		if strings.Contains(got, "Measured engine source tag") != tc.released {
			t.Fatalf("incorrect release claim for %s: %s", tc.provenance, got)
		}
	}
}

func TestNearestRank(t *testing.T) {
	values := []float64{4, 1, 3, 2}
	s := summarize(values)
	if s.N != 4 || s.P50 != 2 || s.P95 != 4 || s.P99 != 4 || values[0] != 4 {
		t.Fatalf("wrong quantiles or mutated samples: %+v %v", s, values)
	}
	values = make([]float64, 100)
	for i := range values {
		values[i] = float64(i + 1)
	}
	s = summarize(values)
	if s.P50 != 50 || s.P95 != 95 || s.P99 != 99 {
		t.Fatalf("wrong hundred-sample ranks: %+v", s)
	}
}
func TestPositiveList(t *testing.T) {
	for _, bad := range []string{"", "0", "-1", "1,nope"} {
		if _, err := positiveList(bad); err == nil {
			t.Fatalf("accepted %q", bad)
		}
	}
}
