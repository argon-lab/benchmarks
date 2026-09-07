package main

import "testing"

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
