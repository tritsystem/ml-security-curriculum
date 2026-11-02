"""Tier-A simulator: multi-agent mesh with bursty legitimate work, planted attacks, and defence arms.
Every number here is an ASSUMPTION about agent systems (listed in ASSUMPTIONS); results are conditional on it."""
import math, os, random, statistics as st
from dataclasses import dataclass, field

ASSUMPTIONS = dict(
    n_agents=8, T=600, warmup=90, attack_window=(120, 480),
    base_rate=(0.2, 1.0),            # legit tool calls/s per agent
    burst_every=180, burst_dur=(15, 90), burst_mult=(5, 10) if os.environ.get("MILD_BURSTS") else (5, 40),
    ratio_sigma=0.6,                 # lognormal noise of tokens-in per action
    burst_ratio_shift=(1.0, 1.0) if os.environ.get("STABLE_RATIO") else (0.2, 5.0),    # batch jobs are ingest-heavy or fan-out-heavy
    reroute_share=0.5,               # a tripped agent's load moves to 2 healthy workers at this share each
    human_latency=(10, 120), human_false_reject=0.02,
)
ROLES = [("orchestrator", {"read", "spawn"}), ("research", {"read", "http_post"}), ("coder", {"read", "write"}),
         ("data", {"read"}), ("reporter", {"read", "http_post"}), ("worker", {"read"}), ("worker", {"read"}),
         ("worker", {"read", "write"})]
SIDE = {"http_post", "write", "spawn"}
CRIT = {"shell", "credential"}
SIDE_SHARE = {"orchestrator": ("spawn", 0.10), "research": ("http_post", 0.05), "coder": ("write", 0.20),
              "reporter": ("http_post", 0.15), "worker": ("write", 0.05)}


def gen_trace(seed):
    """Legit traffic, independent of any defence (common random numbers across arms)."""
    r = random.Random(seed); A = ASSUMPTIONS; T = A["T"]; N = A["n_agents"]
    base = [r.uniform(*A["base_rate"]) for _ in range(N)]
    ratio0 = [math.exp(r.gauss(math.log(3.0), 0.5)) for _ in range(N)]
    mult = [[1.0] * T for _ in range(N)]; rshift = [[1.0] * T for _ in range(N)]
    for i in range(N):
        t = 0
        while True:
            t += int(r.expovariate(1 / A["burst_every"])) + 1
            if t >= T: break
            d = int(r.uniform(*A["burst_dur"])); m = r.uniform(*A["burst_mult"]); sh = r.choice(A["burst_ratio_shift"])
            for k in range(t, min(T, t + d)): mult[i][k] = max(mult[i][k], m); rshift[i][k] = sh
    calls, tok, side = [], [], []
    for i in range(N):
        role = ROLES[i][0]; sname, sfrac = SIDE_SHARE.get(role, (None, 0))
        ci, ti, si = [], [], []
        for k in range(T):
            lam = base[i] * mult[i][k]
            n = poisson(r, lam)
            ns = sum(1 for _ in range(n) if sname and ROLES[i][1] >= {sname} and r.random() < sfrac)
            ci.append(n); si.append(ns)
            ti.append(sum(ratio0[i] * rshift[i][k] * math.exp(r.gauss(0, A["ratio_sigma"])) for _ in range(n)))
        calls.append(ci); tok.append(ti); side.append(si)
    return dict(base=base, ratio0=ratio0, calls=calls, tok=tok, side=side)


def poisson(r, lam):
    if lam > 30:
        return max(0, int(round(r.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= r.random()
        if p <= L: return k
        k += 1


def gen_attack(seed, kind):
    r = random.Random(10_000 + seed * 7 + hash_kind(kind)); A = ASSUMPTIONS
    t0 = r.randint(*A["attack_window"])
    if kind in ("A1", "A4", "A5"): victim = r.choice([1, 4])          # agents allowed to http_post
    else: victim = r.randrange(A["n_agents"])
    ev = []   # (t, agent, tool, n, tokens)
    if kind == "A1":
        ev.append((t0, victim, "read", 3, 400.0))
        for j in range(r.randint(1, 3)): ev.append((t0 + 1 + j, victim, "http_post", 1, 5.0))
    elif kind == "A2":
        for j in range(r.randint(1, 5)): ev.append((t0 + j, victim, r.choice(sorted(CRIT)), 1, 5.0))
    elif kind == "A3":
        rate = r.uniform(30, 100)
        for t in range(t0, min(A["T"], t0 + 120)):
            n = int(rate); ev.append((t, victim, "read", int(n * 0.9), n * 0.9 * 0.3)); ev.append((t, victim, "spawn", n - int(n * 0.9), 1.0))
    elif kind == "A4":
        t = t0
        while t < A["T"]: ev.append((t, victim, "http_post", 1, 3.0)); t += r.randint(20, 60)
    elif kind == "A5":
        infected = {victim: t0}; t = t0; peers = [i for i in range(A["n_agents"]) if i != victim]
        while t < A["T"] - 30 and peers:
            t += r.randint(10, 30); p = peers.pop(r.randrange(len(peers)))
            ev.append((t, victim, "message", 1, 2.0)); infected[p] = t + r.randint(5, 20)
        for p, tp in infected.items():
            for j in range(r.randint(1, 2)):
                if tp + j < A["T"]: ev.append((tp + j, p, "http_post", 1, 5.0))
        return dict(kind=kind, t0=t0, victim=victim, ev=ev, infected=infected)
    elif kind == "A6":
        ev = [(t, None, "fault_proof", 1, 0.0) for t in range(t0, A["T"], 10)]
    return dict(kind=kind, t0=t0, victim=victim, ev=ev, infected={victim: t0})


def hash_kind(kind):  # stable (never Python's randomised hash())
    return sum(ord(c) * (i + 1) for i, c in enumerate(kind))


@dataclass
class Arm:
    name: str
    rate: dict = None        # D1: {"W":..,"c":..}
    cap: bool = False        # D2 capability + approval
    relay: dict = None       # D3a: {"W":..,"tau":..}
    breaker: dict = None     # D3b: {"pick":..,"curve":..,"tms":..}
    droop: dict = None       # {"kp":..,"L0":..}
    random_fp: float = 0.0   # shuffled control: random trips per agent-second
    p_catch: float = 0.8


CURVES = {"SI": (0.02, 0.14), "VI": (1.0, 13.5), "EI": (2.0, 80.0)}   # IEC 60255 standard / very / extremely inverse


def run(seed, kind, arm, trace=None, attack=None):
    A = ASSUMPTIONS; T = A["T"]; N = A["n_agents"]; W0 = A["warmup"]
    trace = trace or gen_trace(seed); attack = attack or (gen_attack(seed, kind) if kind else None)
    r = random.Random(50_000 + seed)
    base = [sum(trace["calls"][i][:W0]) / W0 + 1e-3 for i in range(N)]
    # warm-up calibration for the relay: k = median tokens/action, scale = std of the per-second deviation
    k_i, s_i = [], []
    for i in range(N):
        rat = [trace["tok"][i][t] / trace["calls"][i][t] for t in range(W0) if trace["calls"][i][t]]
        k = st.median(rat) if rat else 3.0; k_i.append(k)
        dev = [trace["tok"][i][t] - k * trace["calls"][i][t] for t in range(W0)]
        s_i.append((st.pstdev(dev) if len(dev) > 1 else 1.0) + 1e-3)
    extra = [[0.0] * T for _ in range(N)]                 # rerouted load (calls/s) added after trips
    tripped = [None] * N; trip_reason = [None] * N
    hist_calls = [[0] * T for _ in range(N)]; hist_tok = [[0.0] * T for _ in range(N)]
    integ = [0.0] * N
    mal = {}                                               # (t, agent) -> list of events
    for e in (attack["ev"] if attack else []):
        mal.setdefault((e[0], e[1]), []).append(e)
    pending = []                                           # (decision_time, agent, malicious?) human approvals
    stats = dict(exfil=0, crit=0, flood_excess=0, legit_actions=0, legit_blocked=0, approvals=0,
                 false_trips=0, cascades=0, contained_t=None, severed_false=0)
    trip_times = []
    for t in range(T):
        for i in range(N):
            if tripped[i] is not None: continue
            # --- legit actions this tick (plus rerouted load) ---
            n_leg = trace["calls"][i][t] + poisson(r, extra[i][t]) if extra[i][t] else trace["calls"][i][t]
            tok_leg = trace["tok"][i][t] + extra[i][t] * k_i[i]
            n_side = trace["side"][i][t]
            evs = mal.get((t, i), [])
            n_mal = sum(e[3] for e in evs if e[2] in ("read", "spawn", "http_post", "shell", "credential", "message"))
            tok_mal = sum(e[4] for e in evs)
            n_tot = n_leg + n_mal
            # --- droop backpressure: throttle when local load exceeds L0 x baseline ---
            keep = 1.0
            if arm.droop:
                L = sum(hist_calls[i][max(0, t - 5):t]) / (5 * base[i])
                if L > arm.droop["L0"]: keep = 1.0 / (1.0 + arm.droop["kp"] * (L - arm.droop["L0"]))
            # --- inline critical-action trip (breaker instantaneous element) ---
            crit_ev = [e for e in evs if e[2] in CRIT]
            if crit_ev and arm.breaker:
                trip(i, t, "instant", tripped, trip_reason, trip_times, attack, stats); continue
            # --- capability control on malicious events ---
            for e in evs:
                tool = e[2]
                if tool == "message":  # injection propagation is a read-like message; not gated
                    continue
                allowed = tool in ROLES[i][1]
                if tool in CRIT:
                    if arm.cap: continue                      # out of scope: blocked
                    stats["crit"] += 1; continue
                if tool in SIDE:
                    if arm.cap:
                        if not allowed: continue
                        stats["approvals"] += e[3]
                        pending.append((t + r.uniform(*A["human_latency"]), i, True, tool, e[3])); continue
                    if tool == "http_post" and r.random() < keep: stats["exfil"] += 1
                    elif tool == "spawn": stats["flood_excess"] += e[3] * keep
                elif tool == "read" and attack and attack["kind"] == "A3":
                    stats["flood_excess"] += e[3] * keep
            # --- legit side-effect actions under capability control ---
            if arm.cap and n_side:
                stats["approvals"] += n_side
                for _ in range(n_side):
                    if r.random() < A["human_false_reject"]: stats["legit_blocked"] += 1
            stats["legit_actions"] += n_leg
            if keep < 1.0: stats["legit_blocked"] += n_leg * (1 - keep)
            exec_calls = n_tot * keep
            hist_calls[i][t] = exec_calls; hist_tok[i][t] = (tok_leg + tok_mal)
            if t < W0: continue
            # --- differential relay ---
            # rolling, burst-robust baselines (deviation 5): median over [t-125, t-5)
            blo, bhi = max(0, t - 125), max(1, t - 5)
            blocks = [sum(hist_calls[i][u:u + 10]) / 10 for u in range(blo, bhi - 9, 10)] or [sum(hist_calls[i][blo:bhi]) / max(1, bhi - blo)]
            base_t = max(st.median(blocks), 0.05)
            if arm.relay:
                rat = [hist_tok[i][u] / hist_calls[i][u] for u in range(blo, bhi) if hist_calls[i][u] > 0]
                k_t = st.median(rat) if rat else k_i[i]
                devs = [sum(hist_tok[i][u:u + 10]) - k_t * sum(hist_calls[i][u:u + 10]) for u in range(blo, bhi - 9, 10)] or [0.0]
                md = st.median(devs); mad = st.median([abs(d - md) for d in devs]) * 1.4826 + 1.0
                Wr = arm.relay["W"]; lo = max(0, t - Wr + 1)
                dI = abs(sum(hist_tok[i][lo:t + 1]) - k_t * sum(hist_calls[i][lo:t + 1]))
                if dI / (mad * math.sqrt((t + 1 - lo) / 10)) > arm.relay["tau"]:
                    trip(i, t, "relay", tripped, trip_reason, trip_times, attack, stats); continue
            # --- inverse-time breaker (IDMT integration) ---
            if arm.breaker:
                Ic = sum(hist_calls[i][max(0, t - 4):t + 1]) / 5
                ratio = Ic / (arm.breaker["pick"] * base_t)
                if ratio > 1.0:
                    a, b = CURVES[arm.breaker["curve"]]
                    den = ratio ** a - 1.0
                    if den > 1e-12: integ[i] += den / (arm.breaker["tms"] * b)   # 1/t_trip; den~0 -> never trips
                else:
                    integ[i] = max(0.0, integ[i] - 0.05)
                if integ[i] >= 1.0:
                    trip(i, t, "breaker", tripped, trip_reason, trip_times, attack, stats); continue
            # --- static rate limit ---
            if arm.rate:
                Wd = arm.rate["W"]
                if sum(hist_calls[i][max(0, t - Wd + 1):t + 1]) > arm.rate["c"] * base_t * Wd:
                    trip(i, t, "rate", tripped, trip_reason, trip_times, attack, stats); continue
            # --- shuffled control: random trips at a fixed rate ---
            if arm.random_fp and r.random() < arm.random_fp:
                trip(i, t, "random", tripped, trip_reason, trip_times, attack, stats); continue
        # human approvals resolve
        still = []
        for (td, i, is_mal, tool, n) in pending:
            if td > t: still.append((td, i, is_mal, tool, n)); continue
            if tripped[i] is not None: continue
            if r.random() < arm.p_catch:
                trip(i, t, "human", tripped, trip_reason, trip_times, attack, stats)
            else:
                if tool == "http_post": stats["exfil"] += 1
                elif tool == "spawn": stats["flood_excess"] += n
        pending = still
        # reroute load of agents tripped this tick to two healthy workers
        for i in range(N):
            if tripped[i] == t:
                healthy = [j for j in range(N) if tripped[j] is None and j != i]
                for j in random.Random(seed * 31 + i).sample(healthy, min(2, len(healthy))):
                    for tt in range(t + 1, T): extra[j][tt] += base[i] * A["reroute_share"]
    # cascades: a non-compromised trip within 60 s after any earlier trip
    comp = set(attack["infected"]) if attack else set()
    for (tt, i, why) in trip_times:
        if i not in comp and any(t2 < tt <= t2 + 60 for (t2, j, _) in trip_times if j != i):
            stats["cascades"] += 1
    stats["trips"] = trip_times
    comp = set(attack["infected"]) if attack else set()
    healthy = [i for i in range(N) if i not in comp] or list(range(N))
    stats["avail"] = sum((tripped[i] if tripped[i] is not None else T) for i in healthy) / (len(healthy) * T)
    stats["true_detect"] = any(i in comp and tt >= attack["infected"][i] for (tt, i, _) in trip_times) if attack else None
    return stats


def trip(i, t, why, tripped, reason, trip_times, attack, stats):
    tripped[i] = t; reason[i] = why; trip_times.append((t, i, why))
    comp = attack["infected"] if attack else {}
    if i in comp and t >= comp[i]:
        if stats["contained_t"] is None: stats["contained_t"] = t - attack["t0"]
    else:
        stats["false_trips"] += 1


def succeeded(kind, s):
    return {"A1": s["exfil"] >= 1, "A2": s["crit"] >= 1, "A3": s["flood_excess"] > 500,
            "A4": s["exfil"] >= 1, "A5": s["exfil"] >= 1}[kind]


def blast(kind, s):
    return {"A1": s["exfil"], "A2": s["crit"], "A3": s["flood_excess"], "A4": s["exfil"], "A5": s["exfil"]}[kind]


# ---------------- decentralized severing under Sybil gossip (A6) ----------------
def run_mesh(seed, quorum, attested=False, n_fake=5):
    """Healthy agents sever a peer once >= quorum distinct reporters sent fault proofs against it.
    Fake nodes (registered identities unless attested) each accuse a random healthy agent every 10 s."""
    A = ASSUMPTIONS; r = random.Random(90_000 + seed); att = gen_attack(seed, "A6")
    accus = {i: set() for i in range(A["n_agents"])}; severed = set(); first = None
    for (t, _, _, _, _) in att["ev"]:
        for f in range(n_fake):
            if attested: continue
            target = r.randrange(A["n_agents"]); accus[target].add(f)
            if len(accus[target]) >= quorum and target not in severed:
                severed.add(target); first = first if first is not None else t - att["t0"]
    return dict(severed=len(severed), first_s=first)
