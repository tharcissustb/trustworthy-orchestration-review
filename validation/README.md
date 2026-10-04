# Bounded mobility-orchestration reproducibility package

This package reproduces the executed illustration reported in the manuscript's evaluation section. It compares a cloud-dependent baseline with an orchestrated condition using identical seeded disturbances.

## Scope

The experiment is a bounded Monte Carlo measurement illustration. It tests whether freshness checking, local fallback, runtime safety gating, recovery handling, and evidence logging can be instantiated and measured. It is not a high-fidelity vehicle model, field trial, certification result, or evidence of real-vehicle safety.

## Run

Python 3.9 or later is sufficient; the script uses only the Python standard library.

```bash
python3 simulate.py
```

The command deterministically regenerates every file in `outputs/`.

## Design

- 100 paired seeds (`1` through `100`)
- 300 control steps per seed at 10 Hz
- identical latency, sensor-error, outage, and braking disturbances for both policies
- Gamma-distributed latency and Gaussian sensor error
- two 5-second cloud outages and two lead-vehicle braking intervals per seed
- fixed deadline of 0.17 seconds
- cloud state considered stale after two control steps
- five required artifact classes: state, latency, freshness, constraint, and decision

All outcomes are generated from the declared disturbance distributions, controller rules, vehicle-gap update, freshness rule, and safety gate. No outcome count is forced to match a manuscript value. The generated summary is therefore the authoritative result for this bounded illustration.

## Outputs

- `seeds.csv`: prespecified random seeds
- `per_step_trace.csv`: 60,000 policy-specific disturbance and event records
- `per_seed_results.csv`: paired seed-level metrics
- `summary.csv`: baseline/orchestrated means, paired differences, and 95% confidence intervals
- `summary.json`: machine-readable summary

## Reproduced results

| Metric | Baseline | Orchestrated | Paired difference |
|---|---:|---:|---:|
| Constraint-violation rate | 0.0053000 | 0.0000000 | -0.0053000 |
| Missed-deadline rate | 0.5054333 | 0.5054333 | 0.0000000 |
| Stale-cloud-action rate | 0.5890000 | 0.0000000 | -0.5890000 |
| Blocked-action rate | 0.0000000 | 0.0000667 | +0.0000667 |
| Cascade index | 0.8375000 | 0.2500000 | -0.5875000 |
| MTTR (s) | 0.3415000 | 0.1000000 | -0.2415000 |
| Trace completeness | 0.4000000 | 1.0000000 | +0.6000000 |

## Metric direction

Lower is preferable for constraint violations, missed deadlines, stale actions, blocked actions, cascade index, and recovery time, except that blocking is an intended safety intervention and must be interpreted jointly with violations. Higher is preferable for trace completeness.

## Confidence intervals

Confidence intervals use the paired seed-level differences and a two-sided 95% normal approximation with the finite-sample critical value 1.984 for 99 degrees of freedom. No interval is informative when every paired difference is identical; such intervals collapse to the point estimate.

Run `python3 verify.py` after `python3 simulate.py` to check row counts, seed coverage, metric bounds, pairing, and exact agreement between the CSV and JSON summaries.
