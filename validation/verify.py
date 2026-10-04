#!/usr/bin/env python3
import csv, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent; OUT=ROOT/"outputs"
cfg=json.loads((ROOT/"config.json").read_text())
with (OUT/"per_step_trace.csv").open() as f: trace=list(csv.DictReader(f))
with (OUT/"per_seed_results.csv").open() as f: seeds=list(csv.DictReader(f))
with (OUT/"summary.csv").open() as f: summary=list(csv.DictReader(f))
summary_json=json.loads((OUT/"summary.json").read_text())["summary"]

checks=[]
def check(name, condition):
    checks.append((name,bool(condition)))
    if not condition: raise AssertionError(name)

nseeds=cfg["seeds"]["stop"]-cfg["seeds"]["start"]+1
check("100 seed rows",len(seeds)==nseeds)
check("two policies x 300 steps x 100 seeds",len(trace)==2*cfg["steps_per_seed"]*nseeds)
check("complete seed sequence",[int(r["seed"]) for r in seeds]==list(range(1,101)))
for r in seeds:
    for k,v in r.items():
        if k!="seed": check(f"bounded {k} seed {r['seed']}",0<=float(v)<=1 or "mttr_seconds" in k)
check("CSV/JSON summary row count",len(summary)==len(summary_json)==7)
for a,b in zip(summary,summary_json):
    check(f"metric order {a['metric']}",a["metric"]==b["metric"])
    for k in ["baseline_mean","orchestrated_mean","paired_difference","ci95_low","ci95_high"]:
        check(f"CSV/JSON equality {a['metric']} {k}",math.isclose(float(a[k]),float(b[k]),rel_tol=0,abs_tol=1e-12))

print("PASS")
print(f"- {len(checks):,} assertions passed")
print(f"- {len(seeds):,} paired seed rows")
print(f"- {len(trace):,} step-level observations")
print(f"- {len(summary):,} summary metrics matched across CSV and JSON")
