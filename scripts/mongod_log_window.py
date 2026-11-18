#!/usr/bin/env python3
"""Sum MongoDB's logged operations inside time windows.  window.py <mongod.log> <label=HH:MM:SS.mmm-HH:MM:SS.mmm> ..."""
import collections, json, re, sys
wins = [(a.split("=")[0], *a.split("=")[1].split("-")) for a in sys.argv[2:]]
tot = {w[0]: collections.Counter() for w in wins}; cnt = {w[0]: collections.Counter() for w in wins}
ex = {w[0]: collections.Counter() for w in wins}
for line in open(sys.argv[1]):
    if '"Slow query"' not in line: continue
    try: d = json.loads(line)
    except Exception: continue
    t = d["t"]["$date"][11:23]; a = d["attr"]; c = a.get("command", {})
    name = next(iter(c), a.get("type", "?"))
    ns = re.sub(r"argon_br_[0-9a-f]+", "argon_br_X", a.get("ns", ""))
    for label, lo, hi in wins:
        if lo <= t <= hi:
            k = (ns, name, a.get("planSummary", ""))
            tot[label][k] += a.get("durationMillis", 0); cnt[label][k] += 1
            ex[label][k] += a.get("docsExamined", 0) or 0
for label, _, _ in wins:
    print(f"== {label}: {sum(cnt[label].values())} operations, {sum(tot[label].values())} ms in the server")
    for k, v in sorted(tot[label].items(), key=lambda x: -x[1])[:8]:
        print(f"   {v:6d} ms {cnt[label][k]:6d} ops {ex[label][k]:9d} docs examined  {k}")
