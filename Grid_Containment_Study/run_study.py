"""Runs the pre-registered study: instrument validation -> fair tuning (seeds 0-19) -> evaluation (seeds 1000-1059)."""
import json, itertools, statistics as st, sys, time, functools
from concurrent.futures import ProcessPoolExecutor
import sim
from sim import Arm

ATTACKS = ["A1", "A2", "A3", "A4", "A5"]
HOURS_PER_RUN = sim.ASSUMPTIONS["T"] / 3600


@functools.lru_cache(maxsize=256)
def _trace(seed): return sim.gen_trace(seed)


def _one(job):
    seed, kind, arm = job
    s = sim.run(seed, kind, arm, trace=_trace(seed))
    return (seed, kind, arm.name, {k: v for k, v in s.items() if k != "trips"},
            None if kind is None else sim.succeeded(kind, s), None if kind is None else sim.blast(kind, s))


def evaluate(arms, seeds, pool):
    jobs = [(s, k, a) for a in arms for s in seeds for k in ATTACKS + [None]]
    out = {}
    for seed, kind, name, stats, succ, bl in pool.map(_one, jobs, chunksize=8):
        out.setdefault(name, []).append((seed, kind, stats, succ, bl))
    return out


def summarize(rows):
    res = {}
    for k in ATTACKS:
        rk = [x for x in rows if x[1] == k]
        cont = [0 if x[3] else 1 for x in rk]; bl = [x[4] for x in rk]
        ttc = [x[2]["contained_t"] for x in rk if x[2]["contained_t"] is not None and not x[3]]
        res[k] = dict(contain=st.mean(cont), contain_sd=st.pstdev(cont), blast=st.mean(bl), blast_sd=st.pstdev(bl),
                      true_detect=st.mean(1 if x[2]["true_detect"] else 0 for x in rk), avail=st.mean(x[2]["avail"] for x in rk),
                      ttc=st.median(ttc) if ttc else None)
    free = [x for x in rows if x[1] is None]
    hrs = len(free) * HOURS_PER_RUN
    res["fp_per_h"] = sum(x[2]["false_trips"] for x in free) / hrs
    res["cascades_per_h"] = sum(x[2]["cascades"] for x in rows) / (len(rows) * HOURS_PER_RUN)
    legit = sum(x[2]["legit_actions"] for x in free) or 1
    res["legit_blocked_frac"] = sum(x[2]["legit_blocked"] for x in free) / legit
    res["approvals_per_h"] = sum(x[2]["approvals"] for x in free) / hrs
    res["mean_contain_A1_A5"] = st.mean(res[k]["contain"] for k in ATTACKS)
    res["mean_true_detect"] = st.mean(res[k]["true_detect"] for k in ATTACKS)
    res["avail_attack_free"] = st.mean(x[2]["avail"] for x in free)
    return res


def tune(family, configs, pool, fp_cap=0.5):
    arms = [Arm(name=f"{family}#{i}", **c) for i, c in enumerate(configs)]
    summ = {a.name: summarize(rows) for a, (name, rows) in zip(arms, sorted(evaluate(arms, range(20), pool).items(), key=lambda kv: int(kv[0].split('#')[1])))}
    feas = [(s["mean_contain_A1_A5"], -s["fp_per_h"], n) for n, s in summ.items() if s["fp_per_h"] <= fp_cap]
    if feas:
        best = max(feas)[2]; ok = True
    else:
        best = min(summ, key=lambda n: summ[n]["fp_per_h"]); ok = False
    i = int(best.split("#")[1])
    return configs[i], summ[best], ok, summ, configs


def validate(cfg_arms):
    """Instrument checks from the pre-registration."""
    out = {}
    # (1) D0 contains nothing
    r = [sim.succeeded(k, sim.run(s, k, Arm("D0"))) for s in range(5) for k in ATTACKS]
    out["D0_contains_nothing"] = all(r)
    # (2) obvious 1000x flood is caught by rate limit and breaker
    def big_flood(seed):
        a = sim.gen_attack(seed, "A3"); v = a["victim"]; t0 = a["t0"]
        a["ev"] = [(t, v, "read", 1000, 300.0) for t in range(t0, t0 + 60)]; return a
    for name in ("D1", "D3b", "D3"):
        arm = cfg_arms[name]
        def trips_fast(s):
            a = big_flood(s); res = sim.run(s, "A3", arm, attack=a)
            return any(i == a["victim"] and a["t0"] <= tt <= a["t0"] + 5 for (tt, i, _) in res["trips"])
        out[f"{name}_trips_1000x_flooder_within_5s"] = all(trips_fast(s) for s in range(5))
    # (3) perfectly regular legit trace -> zero trips
    def flat(seed):
        tr = sim.gen_trace(seed); N = sim.ASSUMPTIONS["n_agents"]; T = sim.ASSUMPTIONS["T"]
        for i in range(N):
            c = max(1, round(tr["base"][i])); tr["calls"][i] = [c] * T; tr["tok"][i] = [c * tr["ratio0"][i]] * T; tr["side"][i] = [0] * T
        return tr
    for name in ("D1", "D3a", "D3b", "D3"):
        out[f"{name}_zero_trips_on_flat_trace"] = all(sim.run(s, None, cfg_arms[name], trace=flat(s))["false_trips"] == 0 for s in range(5))
    return out


def main():
    t_start = time.time(); R = {"assumptions": sim.ASSUMPTIONS}
    with ProcessPoolExecutor() as pool:
        d1_cfgs = [dict(rate=dict(W=W, c=c)) for W in (5, 10, 30) for c in (3, 5, 8, 12, 20, 30, 45, 60, 80, 100)]
        d3a_cfgs = [dict(relay=dict(W=W, tau=tau)) for W in (5, 10, 30) for tau in (3, 5, 8, 12, 20, 30, 45, 60, 80, 100)]
        d3b_cfgs = [dict(breaker=dict(pick=p, curve=cv, tms=m)) for p in (2, 3, 5, 8, 15, 25, 40, 60) for cv in ("SI", "VI", "EI") for m in (0.1, 0.5, 1.0)]
        tuned = {}
        for fam, cfgs in (("D1", d1_cfgs), ("D3a", d3a_cfgs), ("D3b", d3b_cfgs)):
            cfg, summ, ok, allsumm, _ = tune(fam, cfgs, pool)
            tuned[fam] = dict(cfg=cfg, feasible=ok, tuning_summary=summ)
            print(f"[tune] {fam}: {cfg} feasible={ok} contain={summ['mean_contain_A1_A5']:.2f} fp/h={summ['fp_per_h']:.2f}", flush=True)
            if fam == "D3a": d3a_all = sorted(allsumm.items(), key=lambda kv: (kv[1]['fp_per_h'] > 0.5, -kv[1]['mean_contain_A1_A5']))[:3]
            if fam == "D3b": d3b_all = sorted(allsumm.items(), key=lambda kv: (kv[1]['fp_per_h'] > 0.5, -kv[1]['mean_contain_A1_A5']))[:3]
        top_a = [d3a_cfgs[int(n.split('#')[1])]["relay"] for n, _ in d3a_all]
        top_b = [d3b_cfgs[int(n.split('#')[1])]["breaker"] for n, _ in d3b_all]
        d3_cfgs = [dict(relay=ra, breaker=rb, droop=dr) for ra in top_a for rb in top_b
                   for dr in (None, dict(kp=0.5, L0=3), dict(kp=0.2, L0=5))]
        cfg, summ, ok, _, _ = tune("D3", d3_cfgs, pool)
        tuned["D3"] = dict(cfg=cfg, feasible=ok, tuning_summary=summ)
        print(f"[tune] D3: {cfg} feasible={ok} contain={summ['mean_contain_A1_A5']:.2f} fp/h={summ['fp_per_h']:.2f}", flush=True)
        R["tuned"] = {k: dict(cfg=v["cfg"], feasible=v["feasible"]) for k, v in tuned.items()}

        arms = {"D0": Arm("D0"), "D1": Arm("D1", **tuned["D1"]["cfg"]), "D2": Arm("D2", cap=True),
                "D3a": Arm("D3a", **tuned["D3a"]["cfg"]), "D3b": Arm("D3b", **tuned["D3b"]["cfg"]),
                "D3": Arm("D3", **tuned["D3"]["cfg"]), "D4": Arm("D4", cap=True, **tuned["D3"]["cfg"])}
        R["validation"] = validate(arms)
        print("[validate]", R["validation"], flush=True)
        # shuffled control: random trips at D3's tuned false-trip rate
        fp = tuned["D3"]["tuning_summary"]["fp_per_h"]; per_agent_s = fp / 3600 / sim.ASSUMPTIONS["n_agents"]
        arms["RND"] = Arm("RND", random_fp=max(per_agent_s, 1e-7))
        for pc in (0.5, 0.95):
            arms[f"D2_p{pc}"] = Arm(f"D2_p{pc}", cap=True, p_catch=pc)
            arms[f"D4_p{pc}"] = Arm(f"D4_p{pc}", cap=True, p_catch=pc, **tuned["D3"]["cfg"])
        rows = evaluate(list(arms.values()), range(1000, 1060), pool)
        R["eval"] = {n: summarize(rows[n]) for n in arms}
    R["mesh_A6"] = {}
    for label, q, att in (("q=1 (unilateral)", 1, False), ("q=3", 3, False), ("q=3 + attested identities", 3, True)):
        m = [sim.run_mesh(s, q, attested=att) for s in range(1000, 1060)]
        R["mesh_A6"][label] = dict(healthy_severed_mean=st.mean(x["severed"] for x in m),
                                   runs_with_any_sever=sum(1 for x in m if x["severed"]) / len(m),
                                   median_s_to_first=st.median([x["first_s"] for x in m if x["first_s"] is not None]) if any(x["first_s"] is not None for x in m) else None)
    R["runtime_s"] = round(time.time() - t_start, 1)
    import os
    json.dump(R, open("results_mild.json" if os.environ.get("MILD_BURSTS") else "results.json", "w"), indent=1, default=str)
    print("[done]", R["runtime_s"], "s", flush=True)


if __name__ == "__main__":
    main()
