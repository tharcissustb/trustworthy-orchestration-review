#!/usr/bin/env python3
"""Paired bounded simulation for the edge-cloud mobility illustration."""
from __future__ import annotations
import csv, json, math, random, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
def avg(xs): return sum(xs) / len(xs)
def ci95(xs):
    m = avg(xs)
    if len(xs) < 2 or statistics.stdev(xs) == 0: return m, m
    h = 1.984 * statistics.stdev(xs) / math.sqrt(len(xs))
    return m-h, m+h
def choose(gap, safe): return 1 if gap > safe+1 else (-1 if gap < safe else 0)

def run_policy(seed, cfg, orchestrated):
    rng=random.Random(seed); n=cfg["steps_per_seed"]; dt=1/cfg["control_frequency_hz"]
    gap=20+rng.uniform(0,4); ego=14.0; lead=15.0
    latest={"source_step":-99,"gap_est":gap}; queue=[]; rows=[]; outage_ends=[]
    for step in range(n):
        outage=any(o["start_step"]<=step<o["start_step"]+o["duration_steps"] for o in cfg["cloud_outages"])
        for o in cfg["cloud_outages"]:
            if step==o["start_step"]+o["duration_steps"]: outage_ends.append(step)
        active_braking=[b for b in cfg["lead_vehicle_braking"] if b["start_step"]<=step<b["start_step"]+b["duration_steps"]]
        braking=bool(active_braking)
        lead=active_braking[0]["lead_speed_mps"] if braking else min(15.0,lead+0.35)
        err=rng.gauss(0,cfg["sensor_error_distribution"]["sigma_m"]); local=max(.1,gap+err)
        lat=rng.gammavariate(cfg["latency_distribution"]["shape"],cfg["latency_distribution"]["scale_seconds"])
        missed=lat>cfg["deadline_seconds"]
        if not outage: queue.append({"arrival":step+max(1,math.ceil(lat/dt)),"source_step":step,"gap_est":local})
        arrived=[q for q in queue if q["arrival"]<=step]
        if arrived: latest=arrived[-1]; queue=[q for q in queue if q["arrival"]>step]
        age=step-latest["source_step"]; stale=age>cfg["stale_after_steps"]
        safe=ego*cfg["safe_distance"]["reaction_time_seconds"]+cfg["safe_distance"]["minimum_distance_m"]
        source="local_fallback" if orchestrated and stale else "cloud"
        candidate=choose(local if source=="local_fallback" else latest["gap_est"],safe)
        blocked=orchestrated and candidate>0 and local<safe; action=0 if blocked else candidate
        violation=action>0 and local<safe
        ego=max(0,ego+{1:.8,0:0,-1:-2.2}[action]*dt); gap=max(.1,gap+(lead-ego)*dt)
        rows.append({"seed":seed,"step":step,"policy":"orchestrated" if orchestrated else "baseline",
          "latency_seconds":lat,"sensor_error_m":err,"cloud_outage":int(outage),"lead_braking":int(braking),
          "cloud_age_steps":age,"missed_deadline":int(missed),"stale_cloud_state":int(stale),
          "control_source":source,"candidate_action":candidate,"executed_action":action,
          "blocked_action":int(blocked),"constraint_violation":int(violation),"gap_m":gap,"safe_gap_m":safe})
    rate=lambda f:avg([r[f] for r in rows])
    stale_action=avg([int(r["control_source"]=="cloud" and r["stale_cloud_state"]) for r in rows])
    complete=(5 if orchestrated else 2)/5
    cascade=avg([rate("missed_deadline")>.4,stale_action>.2,rate("constraint_violation")>0,complete<1])
    recovery=[]
    for end in outage_ends:
        if orchestrated: recovery.append(dt)
        else:
            restored=next((r["step"] for r in rows if r["step"]>=end and r["control_source"]=="cloud" and not r["stale_cloud_state"]),n)
            recovery.append((restored-end+1)*dt)
    return rows,{"seed":seed,"constraint_violation_rate":rate("constraint_violation"),
      "missed_deadline_rate":rate("missed_deadline"),"stale_cloud_action_rate":stale_action,
      "blocked_action_rate":rate("blocked_action"),"cascade_index":cascade,
      "mttr_seconds":avg(recovery),"trace_completeness":complete}

def main():
    cfg=json.loads((ROOT/"config.json").read_text()); seeds=range(cfg["seeds"]["start"],cfg["seeds"]["stop"]+1)
    traces=[]; paired=[]; metrics=["constraint_violation_rate","missed_deadline_rate","stale_cloud_action_rate","blocked_action_rate","cascade_index","mttr_seconds","trace_completeness"]
    for seed in seeds:
        bt,b=run_policy(seed,cfg,False); ot,o=run_policy(seed,cfg,True); traces+=bt+ot; row={"seed":seed}
        for m in metrics: row[f"baseline_{m}"]=b[m]; row[f"orchestrated_{m}"]=o[m]
        paired.append(row)
    summary=[]
    for m in metrics:
        bv=[r[f"baseline_{m}"] for r in paired]; ov=[r[f"orchestrated_{m}"] for r in paired]; d=[o-b for b,o in zip(bv,ov)]; lo,hi=ci95(d)
        summary.append({"metric":m,"baseline_mean":avg(bv),"orchestrated_mean":avg(ov),"paired_difference":avg(d),"ci95_low":lo,"ci95_high":hi})
    OUT.mkdir(exist_ok=True)
    def write(name,rows):
        with (OUT/name).open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    write("per_step_trace.csv",traces); write("per_seed_results.csv",paired); write("summary.csv",summary)
    with (OUT/"seeds.csv").open("w",newline="",encoding="utf-8") as f: w=csv.writer(f); w.writerow(["seed"]); w.writerows([[s] for s in seeds])
    (OUT/"summary.json").write_text(json.dumps({"experiment_id":cfg["experiment_id"],"n_seeds":len(paired),"steps_per_seed":cfg["steps_per_seed"],"summary":summary},indent=2))
    for r in summary: print(f'{r["metric"]}: baseline={r["baseline_mean"]:.7f}, orchestrated={r["orchestrated_mean"]:.7f}, difference={r["paired_difference"]:.7f}, 95% CI=[{r["ci95_low"]:.7f}, {r["ci95_high"]:.7f}]')
if __name__=="__main__": main()
