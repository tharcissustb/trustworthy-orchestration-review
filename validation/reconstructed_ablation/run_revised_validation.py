#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd, json, math

ROOT = Path(__file__).resolve().parent
config = json.loads((ROOT/"config_revised.json").read_text(encoding="utf-8"))

def simulate(seed, mode, latency_mean=0.204, outage_len=5.0, deadline=0.17):
    rng = np.random.default_rng(seed)
    dt, steps = config["dt_s"], config["steps"]
    ego_v, lead_v = config["ego_initial_speed_mps"], config["lead_initial_speed_mps"]
    gap = rng.uniform(*config["initial_gap_uniform_m"])
    theta = latency_mean / config["latency_gamma_shape"]
    brake_starts = [int(x/dt) for x in config["lead_brake_start_s"]]
    brake_steps = int(round(config["lead_brake_duration_s"]/dt))
    outage_starts = [int(x/dt) for x in config["cloud_outage_start_s"]]
    outage_steps = int(round(outage_len/dt))
    fresh, fallback, gate = mode

    last_cloud_action = 0.0
    cloud_state_age = 999
    queue, rows = [], []
    prev_acc = 0.0
    episode_info = [{"end_step": s+outage_steps, "restore_step": None} for s in outage_starts]

    for t in range(steps):
        if any(s <= t < s + brake_steps for s in brake_starts):
            lead_v = config["lead_brake_target_mps"]
        else:
            lead_v = min(config["lead_initial_speed_mps"], lead_v + 0.6*dt)

        noisy_gap = gap + rng.normal(0.0, config["sensor_sigma_m"])
        latency = rng.gamma(config["latency_gamma_shape"], theta)
        delay_steps = max(1, int(math.ceil(latency/dt)))
        in_outage = any(s <= t < s + outage_steps for s in outage_starts)
        d_safe = ego_v*config["reaction_time_s"] + config["d_min_m"]

        if noisy_gap > d_safe and ego_v < 16.0:
            candidate = 0.8
        elif noisy_gap < d_safe - 1.0:
            candidate = -2.2
        else:
            candidate = 0.0

        if not in_outage:
            queue.append((t + delay_steps, candidate, t))

        due = [q for q in queue if q[0] <= t]
        if due:
            latest = due[-1]
            last_cloud_action = latest[1]
            cloud_state_age = t - latest[2]
            queue = [q for q in queue if q[0] > t]
        else:
            cloud_state_age += 1

        stale = cloud_state_age > config["stale_threshold_steps"]
        action, source = last_cloud_action, "cloud"

        if fresh and stale:
            if fallback:
                action = -2.2 if noisy_gap < d_safe else 0.0
                source = "local_fallback"
            else:
                action = 0.0
                source = "freshness_hold"
        elif fallback and in_outage:
            action = -2.2 if noisy_gap < d_safe else 0.0
            source = "local_fallback"

        blocked = 0
        if gate and action > 0 and noisy_gap < d_safe:
            action = 0.0
            blocked = 1

        violation = int(action > 0 and gap < d_safe)
        stale_action = int(source == "cloud" and stale)

        ego_v = max(0.0, ego_v + action*dt)
        gap = max(0.0, gap + (lead_v - ego_v)*dt)
        jerk = abs(action - prev_acc)/dt
        prev_acc = action

        acceptable_source = (source == "local_fallback") or (source == "cloud" and not stale)
        for ep in episode_info:
            if ep["restore_step"] is None and t >= ep["end_step"] and acceptable_source:
                ep["restore_step"] = t

        rows.append({
            "seed":seed,"step":t,"time_s":t*dt,"latency_s":latency,
            "deadline_exceeded":int(latency>deadline),"outage":int(in_outage),
            "lead_speed_mps":lead_v,"ego_speed_mps":ego_v,"true_gap_m":gap,
            "edge_gap_m":noisy_gap,"d_safe_m":d_safe,"cloud_state_age_steps":cloud_state_age,
            "stale_cloud_action":stale_action,"blocked_action":blocked,
            "constraint_violation_true_gap":violation,"action_mps2":action,
            "source":source,"abs_jerk_mps3":jerk
        })

    df = pd.DataFrame(rows)
    mttrs, censored = [], 0
    for ep in episode_info:
        if ep["restore_step"] is None:
            censored += 1
        else:
            mttrs.append((ep["restore_step"]-ep["end_step"]+1)*dt)
    return df, mttrs, censored

def aggregate_seed(df, mttrs, censored, pname, seed):
    return {
        "policy":pname,"seed":seed,
        "violation_rate":df["constraint_violation_true_gap"].mean(),
        "deadline_exceedance_rate":df["deadline_exceeded"].mean(),
        "stale_action_rate":df["stale_cloud_action"].mean(),
        "blocked_action_rate":df["blocked_action"].mean(),
        "minimum_true_gap_m":df["true_gap_m"].min(),
        "mean_speed_mps":df["ego_speed_mps"].mean(),
        "mean_abs_jerk_mps3":df["abs_jerk_mps3"].mean(),
        "mttr_s":float(np.mean(mttrs)) if mttrs else np.nan,
        "non_recovered_episodes":censored
    }

def main():
    policies = {
        "Baseline": (False,False,False),
        "Freshness only": (True,False,False),
        "Fallback only": (False,True,False),
        "Gate only": (False,False,True),
        "Full": (True,True,True),
    }

    seed_rows, traces = [], []
    for pname, mode in policies.items():
        for seed in config["seeds"]:
            df, mttrs, censored = simulate(seed, mode)
            df["policy"] = pname
            traces.append(df)
            seed_rows.append(aggregate_seed(df, mttrs, censored, pname, seed))

    seed_df = pd.DataFrame(seed_rows)
    trace_df = pd.concat(traces, ignore_index=True)

    summary = []
    metrics = ["violation_rate","deadline_exceedance_rate","stale_action_rate",
               "blocked_action_rate","minimum_true_gap_m","mean_speed_mps",
               "mean_abs_jerk_mps3","mttr_s","non_recovered_episodes"]
    for pname in policies:
        s = seed_df[seed_df.policy==pname]
        row={"policy":pname}
        for col in metrics:
            vals=s[col].dropna().to_numpy()
            mean=vals.mean()
            se=vals.std(ddof=1)/(len(vals)**0.5) if len(vals)>1 else np.nan
            row[col]=mean
            row[col+"_ci_low"]=mean-1.96*se if len(vals)>1 else np.nan
            row[col+"_ci_high"]=mean+1.96*se if len(vals)>1 else np.nan
        summary.append(row)
    pd.DataFrame(summary).to_csv(ROOT/"ablation_summary.csv", index=False)
    seed_df.to_csv(ROOT/"ablation_seed_level.csv", index=False)
    trace_df.to_csv(ROOT/"ablation_step_traces.csv.gz", index=False, compression="gzip")

    sens=[]
    for factor, values in {
        "latency_mean_s":[0.10,0.204,0.30],
        "outage_duration_s":[2.0,5.0,8.0],
        "deadline_s":[0.12,0.17,0.25]
    }.items():
        for value in values:
            rows=[]
            for seed in config["seeds"]:
                kwargs={"latency_mean":0.204,"outage_len":5.0,"deadline":0.17}
                if factor=="latency_mean_s": kwargs["latency_mean"]=value
                elif factor=="outage_duration_s": kwargs["outage_len"]=value
                else: kwargs["deadline"]=value
                df, mttrs, censored = simulate(seed, policies["Full"], **kwargs)
                rows.append(aggregate_seed(df, mttrs, censored, "Full", seed))
            rr=pd.DataFrame(rows)
            rec={"factor":factor,"value":value}
            for c in metrics: rec[c]=rr[c].mean()
            sens.append(rec)
    pd.DataFrame(sens).to_csv(ROOT/"sensitivity_summary.csv", index=False)

if __name__ == "__main__":
    main()
