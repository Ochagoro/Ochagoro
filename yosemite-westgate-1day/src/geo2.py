"""Resolve stops to coordinates via Overpass, which actually has the park features.

Nominatim's free-text search misses most named viewpoints and trailheads inside
Yosemite. Overpass matches on the name tag inside a bounding box, which is what
these are stored as. Everything is printed for review; a wrong pin in the Sierra
is worse than no pin, so unresolved names get a name-search link instead.
"""
import json, re, time, urllib.parse, urllib.request

UA = "ClaudeCode/1.0 yosemite-trip-page (contact: kazushi2002@gmail.com)"
BBOX = "37.35,-121.05,38.30,-119.15"          # south,west,north,east

# key -> exact OSM name to match
WANT = {
    "backwoods":    "Backwoods Burgers",
    "marval":       "Mar-Val Food Store",
    "irondoor":     "Iron Door Saloon",
    "rainbowpool":  "Rainbow Pool Swimming Hole",
    "lodge":        "Yosemite Westgate Lodge",
    "luckybuck":    "Lucky Buck Cafe",
    "rimworld":     "Rim of the World",
    "bigoakflat":   "Big Oak Flat Entrance",
    "craneflat":    "Crane Flat",
    "tuolgrove":    "Tuolumne Grove",
    "valleyview":   "Valley View",
    "tunnelview":   "Tunnel View",
    "bridalveil":   "Bridalveil Fall",
    "villagestore": "Village Store",
    "valleylodge":  "Yosemite Valley Lodge",
    "curry":        "Curry Village",
    "happyisles":   "Happy Isles",
    "swinging":     "Swinging Bridge",
    "glacierpt":    "Glacier Point",
    "sentineldome": "Sentinel Dome",
    "taftpoint":    "Taft Point",
    "washburn":     "Washburn Point",
    "hetchhetchy":  "O'Shaughnessy Dam",
    "olmsted":      "Olmsted Point",
    "tenaya":       "Tenaya Lake",
    "tuolmeadows":  "Tuolumne Meadows",
    "tiogapass":    "Tioga Pass",
    "cooksmeadow":  "Cook's Meadow",
}

names = sorted({v for v in WANT.values()})
alt = "|".join(re.escape(n) for n in names)
Q = f"""[out:json][timeout:120];
(
  node["name"~"^({alt})$"]({BBOX});
  way["name"~"^({alt})$"]({BBOX});
  relation["name"~"^({alt})$"]({BBOX});
);
out center tags;"""

MIRRORS = ["https://overpass-api.de/api/interpreter",
           "https://overpass.kumi.systems/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]
data = None
for attempt in range(3):
    for m in MIRRORS:
        try:
            req = urllib.request.Request(m, data=urllib.parse.urlencode({"data": Q}).encode(),
                                         headers={"User-Agent": UA})
            data = json.load(urllib.request.urlopen(req, timeout=180))
            print("via", m); break
        except Exception as e:
            print("  fail", m.split("/")[2], type(e).__name__, getattr(e, "code", ""))
    if data: break
    time.sleep(5)
if data is None:
    raise SystemExit("all Overpass mirrors failed")

found = {}
for el in data["elements"]:
    nm = el.get("tags", {}).get("name")
    lat = el.get("lat") or (el.get("center") or {}).get("lat")
    lon = el.get("lon") or (el.get("center") or {}).get("lon")
    if not nm or lat is None:
        continue
    tags = el.get("tags", {})
    kind = (tags.get("tourism") or tags.get("amenity") or tags.get("natural")
            or tags.get("shop") or tags.get("leisure") or tags.get("mountain_pass")
            or tags.get("place") or el["type"])
    found.setdefault(nm, []).append((round(lat, 5), round(lon, 5), kind, el["type"]))

out = {}
for key, nm in WANT.items():
    hits = found.get(nm, [])
    if not hits:
        print(f"{key:14} — not found: {nm!r}")
        continue
    # prefer a viewpoint/attraction/shop node over a generic area
    hits.sort(key=lambda h: (h[3] != "node",))
    lat, lon, kind, typ = hits[0]
    out[key] = {"lat": lat, "lon": lon, "name": nm}
    extra = f"  (+{len(hits)-1} more)" if len(hits) > 1 else ""
    print(f"{key:14} {lat:>9.5f},{lon:>11.5f}  {kind:16} {nm}{extra}")

json.dump(out, open("geo.json", "w"), indent=1)
print(f"\nresolved {len(out)}/{len(WANT)}")
