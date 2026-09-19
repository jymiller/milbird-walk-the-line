"""Two independent detectors, one verdict.

Colour detection runs locally and deterministically. Memories.ai runs in the
cloud and answers a description. Where they agree, the locate is real. Where
they disagree, a human looks. That disagreement is the product.

    compare.py locates.geojson memories_locates.json
"""
import json, sys, os

WINDOW = 4.0   # seconds either side counts as the same moment


def load_local(p):
    if not os.path.exists(p):
        return []
    g = json.load(open(p))
    out = []
    for f in g.get("features", []):
        pr = f.get("properties", {})
        if pr.get("t") is not None:
            out.append({"t": float(pr["t"]), "colour": pr.get("primary"),
                        "utility": pr.get("utility"), "area": pr.get("area")})
    return sorted(out, key=lambda x: x["t"])


def load_remote(p):
    if not os.path.exists(p):
        return []
    d = json.load(open(p))
    out = []
    for h in d.get("hits", []):
        s, e = h.get("start"), h.get("end")
        if s is None:
            continue
        out.append({"t": float(s), "end": float(e) if e is not None else float(s),
                    "score": h.get("score"), "snippet": (h.get("snippet") or "")[:60]})
    return sorted(out, key=lambda x: x["t"])


def main():
    loc = load_local(sys.argv[1] if len(sys.argv) > 1 else "locates.geojson")
    rem = load_remote(sys.argv[2] if len(sys.argv) > 2 else "memories_locates.json")

    if not loc and not rem:
        sys.exit("neither detector produced output")
    if not rem:
        print(f"colour detection only: {len(loc)} marks. No second opinion to check it against.")
        print("Every one of these is UNCORROBORATED — one detector is an assertion, not evidence.")
        return
    if not loc:
        print(f"memories.ai only: {len(rem)} moments, no colour corroboration.")
        return

    both, local_only = [], []
    matched_remote = set()
    for L in loc:
        hit = None
        for i, R in enumerate(rem):
            if R["t"] - WINDOW <= L["t"] <= R["end"] + WINDOW:
                hit = (i, R)
                break
        if hit:
            matched_remote.add(hit[0])
            both.append((L, hit[1]))
        else:
            local_only.append(L)
    remote_only = [R for i, R in enumerate(rem) if i not in matched_remote]

    print(f"colour detector : {len(loc)} marks")
    print(f"memories.ai     : {len(rem)} moments")
    print()
    print(f"  CONFIRMED  both agree      {len(both):>3}   → high confidence, auto-proposable")
    print(f"  COLOUR ONLY not described  {len(local_only):>3}   → paint the model did not describe")
    print(f"  MODEL ONLY  no paint found {len(remote_only):>3}   → described but no locate colour present")
    print()

    if both:
        print("CONFIRMED — two independent methods, same moment:")
        for L, R in both[:8]:
            print(f"   t={L['t']:>6.1f}s  {L['colour']:<7} ({L['utility']})   "
                  f"model score={R['score']}  {R['snippet']}")
    if local_only:
        print("\nCOLOUR ONLY — needs a human:")
        for L in local_only[:6]:
            print(f"   t={L['t']:>6.1f}s  {L['colour']:<7} area={L['area']}")
    if remote_only:
        print("\nMODEL ONLY — described a marking where no locate colour was found:")
        for R in remote_only[:6]:
            print(f"   t={R['t']:>6.1f}s  score={R['score']}  {R['snippet']}")

    agree = len(both) / max(1, len(loc)) * 100
    print(f"\nagreement: {agree:.0f}% of colour detections corroborated")
    print("The disagreements are the review queue. That is the point:")
    print("one detector is an assertion; two that agree is evidence.")

    json.dump({"confirmed": [{"t": L["t"], "colour": L["colour"], "score": R["score"]}
                             for L, R in both],
               "colour_only": local_only, "model_only": remote_only,
               "agreement_pct": round(agree, 1)},
              open("agreement.json", "w"), indent=1)
    print("\n  agreement.json")


if __name__ == "__main__":
    main()
