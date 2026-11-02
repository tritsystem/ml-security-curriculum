"""EXPLORATORY (not pre-registered): (1) the practical combination D2 + feasible flood detector; (2) relay when the
tokens-in/actions-out ratio is stable (the report's own premise). Same eval seeds 1000-1059."""
import json, os
from concurrent.futures import ProcessPoolExecutor
import run_study as rs
from sim import Arm

if __name__ == "__main__":
    R = json.load(open("results.json")); t = R["tuned"]
    out = {}
    with ProcessPoolExecutor() as pool:
        if not os.environ.get("STABLE_RATIO"):
            arms = [Arm("D2+D1", cap=True, **t["D1"]["cfg"]), Arm("D2+D3b", cap=True, **t["D3b"]["cfg"]),
                    Arm("D2+D1+D3b", cap=True, **t["D1"]["cfg"], **t["D3b"]["cfg"])]
            rows = rs.evaluate(arms, range(1000, 1060), pool)
            out["combos"] = {a.name: rs.summarize(rows[a.name]) for a in arms}
        else:
            cfgs = [dict(relay=dict(W=W, tau=tau)) for W in (5, 10, 30) for tau in (3, 5, 8, 12, 20, 30, 45, 60, 80, 100)]
            cfg, summ, ok, _, _ = rs.tune("D3a", cfgs, pool)
            rows = rs.evaluate([Arm("D3a_stable", **cfg), Arm("D1_stable", **t["D1"]["cfg"])], range(1000, 1060), pool)
            out["stable_ratio_relay"] = dict(cfg=cfg, feasible=ok, eval=rs.summarize(rows["D3a_stable"]),
                                             d1_same_traffic=rs.summarize(rows["D1_stable"]))
    fn = "exploratory_stable_ratio.json" if os.environ.get("STABLE_RATIO") else "exploratory_combos.json"
    json.dump(out, open(fn, "w"), indent=1, default=str); print("wrote", fn)
