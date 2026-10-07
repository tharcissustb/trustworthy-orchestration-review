# Revised mobility validation — Tier 1, Item 5

This package adds:
- an independent **true-gap** violation outcome while the runtime gate sees the **noisy edge estimate**;
- four component ablations plus the original baseline: Freshness only, Fallback only, Gate only, Full;
- cost/behavior metrics: minimum true gap, mean ego speed, mean absolute jerk;
- censored/non-recovered episode reporting;
- one-factor-at-a-time sensitivity sweeps for latency mean, outage duration, and deadline.

## Important provenance note
The supplied manuscript/workbook describe the numerical parameters but the executable GitHub source was not connected in this session. Therefore this package is a **reconstructed revised validation model** from the stated parameters, with explicit event timing and controller rules recorded in `config_revised.json`.

Before replacing the canonical repository validation outputs, reconcile `run_revised_validation.py` with the existing repository simulator. Do not present these numbers as reruns of the original repository code unless that reconciliation is completed.

## Run
```bash
python run_revised_validation.py
```

Outputs:
- `ablation_summary.csv`
- `ablation_seed_level.csv`
- `ablation_step_traces.csv.gz`
- `sensitivity_summary.csv`

## Core revised definition
A safety violation is counted when acceleration is executed while the **true simulated gap** is below `d_safe`. The safety gate itself sees only the **noisy estimated gap**. This prevents the evaluation predicate from being identical to the gate predicate.
