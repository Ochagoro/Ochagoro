"""Resolve every stop to coordinates via OpenStreetMap Nominatim.

A wrong pin in the Sierra is worse than no pin, so every result is bounds
checked against the corridor and printed for review. Anything that misses
gets no coordinate and falls back to a name search in the page.
"""
import json, time, urllib.parse, urllib.request

UA = "ClaudeCode/1.0 yosemite-trip-page (contact: kazushi2002@gmail.com)"
# Mountain View through Tioga Pass, generously padded
BOUNDS = (37.35, 38.30, -121.00, -119.15)   # latmin, latmax, lonmin, lonmax

QUERIES = [
    ("backwoods",   "Backwoods Burgers, 1214 W F St, Oakdale, California"),
    ("marval",      "Mar-Val Food Stores, 19000 Main Street, Groveland, California"),
    ("irondoor",    "Iron Door Saloon, 18761 Main Street, Groveland, California"),
    ("rainbowpool", "Rainbow Pool, Tuolumne County, California"),
    ("lodge",       "Yosemite Westgate Lodge, 7633 State Highway 120, Groveland, California"),
    ("luckybuck",   "Lucky Buck Cafe, 7647 State Highway 120, Groveland, California"),
    ("rimworld",    "Rim of the World Vista, Stanislaus National Forest, California"),
    ("bigoakflat",  "Big Oak Flat Entrance Station, Yosemite National Park"),
    ("craneflat",   "Crane Flat, Yosemite National Park, California"),
    ("tuolgrove",   "Tuolumne Grove, Yosemite National Park, California"),
    ("valleyview",  "Valley View, Yosemite National Park, California"),
    ("tunnelview",  "Tunnel View, Yosemite National Park, California"),
    ("bridalveil",  "Bridalveil Fall, Yosemite National Park, California"),
    ("village",     "Yosemite Village, Yosemite National Park, California"),
    ("valleylodge", "Yosemite Valley Lodge, Yosemite National Park, California"),
    ("curry",       "Curry Village, Yosemite National Park, California"),
    ("happyisles",  "Happy Isles, Yosemite National Park, California"),
    ("swinging",    "Swinging Bridge, Yosemite Valley, California"),
    ("glacierpt",   "Glacier Point, Yosemite National Park, California"),
    ("sentineldome","Sentinel Dome, Yosemite National Park, California"),
    ("taftpoint",   "Taft Point, Yosemite National Park, California"),
    ("washburn",    "Washburn Point, Yosemite National Park, California"),
    ("hetchhetchy", "O'Shaughnessy Dam, Hetch Hetchy, Yosemite National Park"),
    ("olmsted",     "Olmsted Point, Yosemite National Park, California"),
    ("tenaya",      "Tenaya Lake, Yosemite National Park, California"),
    ("tuolmeadows", "Tuolumne Meadows, Yosemite National Park, California"),
    ("tiogapass",   "Tioga Pass, Yosemite National Park, California"),
    ("cooksmeadow", "Cook's Meadow, Yosemite Valley, California"),
]

def lookup(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 3, "addressdetails": 0})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))

out = {}
for key, q in QUERIES:
    try:
        hits = lookup(q)
    except Exception as e:
        print(f"{key:14} ERROR {e}")
        time.sleep(1.2); continue
    picked = None
    for h in hits:
        lat, lon = float(h["lat"]), float(h["lon"])
        if BOUNDS[0] <= lat <= BOUNDS[1] and BOUNDS[2] <= lon <= BOUNDS[3]:
            picked = (round(lat, 5), round(lon, 5), h.get("display_name", "")[:72])
            break
    if picked:
        out[key] = {"lat": picked[0], "lon": picked[1], "osm": picked[2]}
        print(f"{key:14} {picked[0]:>9.5f},{picked[1]:>11.5f}  {picked[2]}")
    else:
        print(f"{key:14} NO IN-BOUNDS MATCH  (hits={len(hits)})"
              + (f"  first={hits[0].get('display_name','')[:60]}" if hits else ""))
    time.sleep(1.2)

json.dump(out, open("geo.json", "w"), indent=1)
print(f"\nresolved {len(out)}/{len(QUERIES)}")
