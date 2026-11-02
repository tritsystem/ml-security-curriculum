# Results: "Electrical grid" containment for multi-agent security vs plain baselines (Tier A, simulator)

2026-10-30. Pre-registration: `PRE_REGISTRATION.md`, including 6 dated deviations. **All results are conditional on a
stochastic simulator** (assumptions in `sim.py`); none are measured on real LLM agents. Evaluation: 60 seeds per
attack plus 60 attack-free runs (8 agents, 600 s each). Every arm is tuned on separate seeds to ≤ 0.5 false trips per
hour fleet-wide where possible. Raw data: `results.json`, `results_mild.json`, `exploratory_*.json`.

## Headline
**The report's central claim is not supported in this setting.**
- **The full grid design (relay + breaker + droop) could not be tuned to a usable false-alarm rate.** At its best it
  makes 48 false trips per hour and leaves about 20% of the fleet available. Its apparent 97% "containment" is cluster
  collapse: it trips the compromised agent *after* compromise in only 4–8% of runs.
- **The parts that can run within budget add nothing over plain controls.** The inverse-time breaker ties a static
  rate limit on floods. Its "instant trip on critical tools" rule is a capability check in disguise. It scores 0% on
  all three data-theft attacks.
- **Capability control with human approval dominates theft and escalation,** at an unworkable approval cost.
- **One conditional positive (exploratory):** if an agent's tokens-in/actions-out ratio is stable (the report's own
  premise), the differential relay becomes usable and beats a rate limit on floods (92% vs 50%) and on one-shot theft
  (32% vs 0%). Whether real agents have a stable ratio is the open, measurable question.

## Main results (bursts up to 40× baseline): containment rate (blast radius)
| Arm | A1 one-shot theft | A2 escalation | A3 flood | A4 trickle theft | A5 lateral spread | Mean | False trips/h | Availability |
|---|---|---|---|---|---|---|---|---|
| D0 none | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.0 | 1.00 |
| D1 rate limit | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.10 | 0.2 | 1.00 |
| D2 capability + approval | **0.88** | **1.00** | 0.02 | **0.73** | **0.68** | 0.66 | 0.0 | 1.00 |
| D3a relay (cannot reach budget) | 0.52 | 0.33 | 0.60 | 0.30 | 0.00 | 0.35 | **29.9** | 0.66 |
| D3b breaker | 0.00 | 1.00 | 0.50 | 0.00 | 0.00 | 0.30 | 0.1 | 1.00 |
| D3 full grid (cannot reach budget) | 0.98* | 1.00* | 1.00* | 0.93* | 0.93* | 0.97* | **48.0** | **0.19** |
| D4 = D2 + D3 | 1.00* | 1.00* | 1.00* | 1.00* | 0.98* | 1.00* | **48.0** | **0.20** |
| RND control (random trips) | 0.10 | 0.25 | 0.32 | 0.22 | 0.00 | 0.18 | 28.9 | 0.71 |

\* Collapse artifact: the compromised agent is usually already tripped before the attack (true-detection 4–8%).
D2 approval burden: **≈ 7,600 human approvals per hour** (3,100 with milder bursts). p_catch sensitivity: mean 0.46
(p = 0.5) to 0.76 (p = 0.95). Milder bursts (5–10×, exploratory) give the same picture; floods get easier for D1 and
D3b (0.82 / 0.83). Sybil gossip (A6): healthy agents severed, mean of 8 = **8.0** (unilateral), **7.95** (quorum 3),
**0** (attested identities).

## Exploratory (not pre-registered)
- D2 + rate limit = D2 + breaker = 0.76 mean containment, 0.1–0.2 false trips/h, full availability. **The breaker adds
  nothing over a rate limit.**
- Stable-ratio traffic: relay tunable (0.1 false trips/h); A1 0.32, A3 0.92, mean 0.25, against rate limit A3 0.50,
  mean 0.10.

## Pre-registered predictions: what held
| Prediction | Result |
|---|---|
| A1: rate limit ~0, capability ~80%, grid 5–15% | **Held** (0.00 / 0.88 / 0.00 for the feasible breaker) |
| A2: capability ~100%, grid ~100% via instant trip | **Held** (1.00 / 1.00; the grid's win is a capability rule) |
| A3: rate limit ~95%, grid ~95% | **Wrong**: 0.50 each. Legitimate bursts mask floods for any rate-based detector |
| A3: capability ~10% | **Held** (0.02) |
| A4: rate limit 0, capability ~80%, grid 0–10% | **Held** (0.00 / 0.73 / 0.00) |
| A5: capability high, grid ~30% | **Partial**: capability 0.68; grid **0.00** (worse than predicted) |
| Grid false trips ≥ rate limit at equal containment | **Held, more strongly than expected**: the relay can't reach the budget at all |
| Droop reduces cascades | **Not supported**: tuning never selected droop; untestable because D3 was infeasible |
| Quorum q = 3 substantially reduces Sybil severing | **Wrong**: 7.95 vs 8.0. Only attested identities help |
| Overall: grid helps only on floods and cascades; capability dominates theft | **Mostly held, stronger negative**: the grid didn't beat a rate limit even on floods |

## Instrument history (honesty note)
Four runs were needed before the instrument was valid: tuning grids too narrow; a metric that rewarded cluster
collapse; a mis-specified validation check; fragile one-shot baselines (every detector); and a median of sparse counts
equal to 0. Each fix applied to all arms equally and is recorded as a dated deviation. Earlier results are kept
(`results_run*`). Final validation passed: D0 contains nothing; the rate limit and breaker trip a 1000× flooder within
5 s; every detector stays silent on flat traffic.

## Limits
Simulated traffic, attacks and human behaviour. The burst sizes, in/out ratio shifts and approval latency are
assumptions that drive the results. One approval model (every side-effect action). No real LLM agents yet.

## What this means for the report
1. Lead with capability controls: least privilege, re-authentication at handoffs, verified identities. They stop
   theft and escalation; flow analysis doesn't.
2. Approval must be selective (e.g. new egress destinations only). Approving every action doesn't scale.
3. Keep flow detection for floods, as a plain rate limit. The grid vocabulary added no measured benefit.
4. The differential relay is worth a real test, but only after measuring whether real agents have a stable
   tokens-in/actions-out ratio.
5. Gossip severing needs attested identities; quorum alone fails against Sybils.

## Next (Tier B)
Instrument real agents behind mcp-gateway. Log tokens-in and actions-out per agent per second over a week of normal
use, and measure ratio stability. If it is stable, rerun the relay against planted prompt-injection attacks.
