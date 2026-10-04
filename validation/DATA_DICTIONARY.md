# Data dictionary

## Per-step trace

| Variable | Definition |
|---|---|
| `seed` | Paired simulation seed |
| `step` | Control step, 0–299 |
| `latency_seconds` | Gamma-generated communication latency |
| `sensor_error_m` | Gaussian sensor error in metres |
| `cloud_outage` | 1 during a scheduled outage |
| `lead_braking` | 1 during a scheduled braking interval |
| `missed_deadline` | 1 for a selected latency deadline exceedance |
| `baseline_stale_action` | 1 when the baseline executes a stale cloud action |
| `baseline_constraint_violation` | 1 when the baseline executes a constraint-violating action |
| `orchestrated_blocked_action` | 1 when the runtime gate blocks a candidate action |

## Per-seed results

All rate variables are event counts divided by 300 eligible control steps. Cascade index is the fraction of four monitored components whose adverse threshold is crossed. MTTR is seconds from outage end to restoration of an acceptable control source. Trace completeness is the fraction of five required artifact classes present and linkable.
