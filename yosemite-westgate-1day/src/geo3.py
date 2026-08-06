"""Resolve the stragglers so no link depends on a network name lookup.

A search link (?q=…) needs connectivity to resolve. Inside the park there is
none, so every destination has to carry its own coordinate.
"""
import json, re, time, urllib.parse, urllib.request

UA = "ClaudeCode/1.0 yosemite-trip-page (contact: kazushi2002@gmail.com)"
MIRRORS = ["https://overpass.kumi.systems/api/interpreter",
           "https://overpass-api.de/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]

OAKDALE   = "37.72,-120.90,37.80,-120.78"     # s,w,n,e
GROVELAND = "37.81,-120.28,37.87,-120.20"
YOSVALLEY = "37.72,-119.62,37.77,-119.54"
BIGOAKGATE= "37.75,-120.00,37.83,-119.85"

Q = f"""[out:json][timeout:120];
(
  node["name"~"Backwoods",i]({OAKDALE});
  way ["name"~"Backwoods",i]({OAKDALE});
  node["name"~"Mar.?Val",i]({GROVELAND});
  way ["name"~"Mar.?Val",i]({GROVELAND});
  node["name"~"Degnan",i]({YOSVALLEY});
  way ["name"~"Degnan",i]({YOSVALLEY});
  node["name"~"Village Grill",i]({YOSVALLEY});
  way ["name"~"Village Grill",i]({YOSVALLEY});
  node["name"~"Big Oak Flat",i]({BIGOAKGATE});
  way ["name"~"Big Oak Flat",i]({BIGOAKGATE});
  node["barrier"="toll_booth"]({BIGOAKGATE});
  node["entrance"]["name"]({BIGOAKGATE});
);
out center tags;"""

data = None
for attempt in range(3):
    for m in MIRRORS:
        try:
            req = urllib.request.Request(m, data=urllib.parse.urlencode({"data": Q}).encode(),
                                         headers={"User-Agent": UA})
            data = json.load(urllib.request.urlopen(req, timeout=180))
            print("via", m.split("/")[2]); break
        except Exception as e:
            print("  fail", m.split("/")[2], type(e).__name__, getattr(e, "code", ""))
    if data: break
    time.sleep(5)
if data is None:
    raise SystemExit("all Overpass mirrors failed")

for el in data["elements"]:
    t = el.get("tags", {})
    lat = el.get("lat") or (el.get("center") or {}).get("lat")
    lon = el.get("lon") or (el.get("center") or {}).get("lon")
    if lat is None:
        continue
    kind = (t.get("amenity") or t.get("shop") or t.get("barrier")
            or t.get("tourism") or t.get("entrance") or el["type"])
    print(f"  {round(lat,5):>9},{round(lon,5):>11}  {kind:14} {t.get('name','(unnamed)')}")
