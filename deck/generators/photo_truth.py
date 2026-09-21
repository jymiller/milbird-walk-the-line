"""Ground truth for the 53 GPS-tagged photos, judged by eye on 20 Sep 2026.

Every photo was opened and looked at. The verdict below is a human call, not a
detector output — that is the whole point of it. GPS is EXIF from the camera:
measured, not reconstructed.

  locate    the photo shows utility locate paint on the ground
  clear     street-level photo of the ground, no locate paint on it
  offsite   not the street at all (the hackathon venue, screens, posters)
  people    a person, not the ground

`colours` are APWA colours actually visible in the frame, dominant first.
`note` says what is in the picture, in plain words.
"""
import json, os

T = {
    # --- the hackathon venue: Apache Doris / VeloDB / EdgeOne booths, screens, whiteboard
    "IMG_2094": ("offsite", [], "Doris booth, three people in front of the banner"),
    "IMG_2095": ("offsite", [], "same booth, second frame"),
    "IMG_2096": ("offsite", [], "VeloDB poster, 'Born for Real-Time, Ready for AI'"),
    "IMG_2097": ("offsite", [], "VeloDB use-cases poster"),
    "IMG_2098": ("offsite", [], "VeloDB Cloud / Enterprise poster"),
    "IMG_2099": ("offsite", [], "'Trusted by over 10,000 companies' poster"),
    "IMG_2100": ("offsite", [], "Doris ecosystem poster"),
    "IMG_2101": ("offsite", [], "whiteboard, free wifi and memories.ai"),
    "IMG_2102": ("offsite", [], "tote bag, stickers and a QR survey on a table"),
    "IMG_2103": ("offsite", [], "EdgeOne Makers pull-up banner"),
    "IMG_2105": ("offsite", [], "talk slide on a wall screen"),
    "IMG_2106": ("offsite", [], "talk slide, governance"),
    "IMG_2107": ("offsite", [], "talk slide, maintainability"),
    "IMG_2108": ("offsite", [], "talk slide, second frame"),
    "IMG_2109": ("offsite", [], "talk slide, bottom of the grid"),
    "IMG_2110": ("offsite", [], "panel slide, Building the executable AI stack"),

    # --- the street
    "IMG_2112": ("clear",  [],
                 "724 Pine St front door, open. The walk starts here."),
    "IMG_2113": ("locate", ["red"],
                 "red paint on the slab, letters and a bar, hard shadow across it"),
    "IMG_2114": ("locate", ["green", "red"],
                 "green line run along the slab joint, red marks beside it"),
    "IMG_2115": ("locate", ["red", "green"],
                 "red marks and a green edge line at the base of a pole"),
    "IMG_2116": ("locate", ["red"],
                 "red marks beside a PG&E vault cover"),
    "IMG_2117": ("people", [], "two people, selfie"),
    "IMG_2118": ("locate", ["yellow", "red"],
                 "yellow GAS written on the slab with a red arrow beside it"),
    "IMG_2119": ("locate", ["red", "green"],
                 "red marks with green dots, kerb and vault"),
    "IMG_2120": ("locate", ["green", "red", "orange"],
                 "green line along the slabs, red lettering, orange fleck"),
    "IMG_2121": ("locate", ["green"],
                 "green edging beside a PG&E GAS VALVE cover"),
    "IMG_2122": ("locate", ["green"], "green marks along the slab by a vault"),
    "IMG_2123": ("locate", ["green"], "green marks along the brick edge"),
    "IMG_2124": ("locate", ["green", "red"],
                 "green line across the walk at a tree pit, small red mark"),
    "IMG_2125": ("clear",  [], "white graffiti scrawl on the slab — not a locate"),
    "IMG_2126": ("clear",  [], "graffiti tags over a grate, one blue smear"),
    "IMG_2127": ("clear",  [], "graffiti tags over a vault lid"),
    "IMG_2128": ("people", [], "shoulder and a name badge"),
    "IMG_2129": ("locate", ["green"], "green edging along the slabs by a tree"),
    "IMG_2130": ("locate", ["green"], "green edging, second frame"),
    "IMG_2131": ("locate", ["red"],
                 "red offset ticks with 12 KV written under them"),
    "IMG_2132": ("locate", ["red"],
                 "red offset ticks, 12 KV and a depth figure"),
    "IMG_2133": ("clear",  [], "bare slabs, a shoe, one white arrow at the top edge"),
    "IMG_2134": ("locate", ["red"], "red tick and a run of figures along the slab"),
    "IMG_2136": ("locate", ["red"], "red offset tick, faded"),
    "IMG_2137": ("locate", ["red"], "red offset tick mid-slab"),
    "IMG_2138": ("locate", ["red", "yellow"],
                 "red arcs with yellow GAS lettering beside them"),
    "IMG_2139": ("locate", ["red", "yellow"],
                 "faded red run with lettering, a yellow mark by the manhole"),
    "IMG_2140": ("locate", ["red"], "faded red run down the slabs past a tree"),
    "IMG_2141": ("locate", ["red"], "faded red marks along the walk"),
    "IMG_2142": ("locate", ["red"], "faded red marks and a white box outline"),
    "IMG_2143": ("locate", ["red"], "red marks beside a storm grate"),
    "IMG_2144": ("locate", ["white"],
                 "white USA stencil — Underground Service Alert, the 811 request mark"),
    "IMG_2145": ("people", [], "person walking, street scene"),
    "IMG_2146": ("people", [], "person walking, second frame"),
    "IMG_2147": ("people", [], "person on a phone on the sidewalk"),
    "IMG_2148": ("clear",  [], "plain concrete and steps"),
    "IMG_2149": ("locate", ["white"], "white arrow at a building corner"),
}

if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    gps = {os.path.splitext(r["file"])[0]: r for r in json.load(open(f"{HERE}/gps.json"))}
    missing = set(gps) ^ set(T)
    assert not missing, f"photo/judgement mismatch: {missing}"

    out = []
    for k, (verdict, colours, note) in T.items():
        g = gps[k]
        out.append({"id": k, "verdict": verdict, "colours": colours, "note": note,
                    "lat": g["lat"], "lon": g["lon"], "at": g["at"]})
    out.sort(key=lambda r: r["id"])
    json.dump(out, open(f"{HERE}/truth.json", "w"), indent=1)

    from collections import Counter
    c = Counter(r["verdict"] for r in out)
    cols = Counter(x for r in out for x in r["colours"])
    print("53 photos judged by eye")
    for k, v in c.most_common():
        print(f"  {k:<8} {v}")
    print("colours seen on the ground:", dict(cols))
    loc = [r for r in out if r["verdict"] == "locate"]
    lats = [r["lat"] for r in loc]; lons = [r["lon"] for r in loc]
    print(f"positives span {(max(lats)-min(lats))*111320:.0f} m N-S, "
          f"{(max(lons)-min(lons))*88000:.0f} m E-W")
