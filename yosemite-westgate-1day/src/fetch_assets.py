import io, json, os, re, time, urllib.parse, urllib.request
from PIL import Image
UA = "ClaudeCode/1.0 (yosemite one-day plan page)"
os.makedirs("img", exist_ok=True)

def get(url, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2.5 * (i + 1))

def api(params):
    return json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))

# key, commons title, fetch width, output width, webp quality
WANT = [
  ("hero_tunnelview","File:“Tunnel View” overlook showing famous rock formations in Yosemite Valley 03.jpg",1600,1500,68),
  ("valleyview",     "File:Valley View Yosemite August 2013 002.jpg",           1200, 950, 66),
  ("bridalveil",     "File:Yosemite National Park, Bridalveil Fall, 2024-07 CN-01.jpg", 900, 760, 66),
  ("halfdome_gp",    "File:Half Dome from Glacier Point, Yosemite NP - Diliff.jpg", 1400,1200, 68),
  ("gp_sunset",      "File:Glacier Point View of Half Dome at Sunset at Yosemite National Park.jpg",1200,1000,68),
  ("sequoia",        "File:Looking up biggest in Tuolumne Grove.jpg",            900, 760, 66),
  ("tenaya",         "File:Lake Tenaya in Yosemite NP.jpg",                     1200, 950, 66),
  ("olmsted",        "File:Olmsted Point Yosemite August 2013 002.jpg",         1200, 950, 66),
  ("taftpoint",      "File:Taft Point, Yosemite Valley (Unsplash xS-lvhpiJNM).jpg",1200, 950, 66),
  ("stars",          "File:Yosemite cliff under stars (Unsplash).jpg",          1400,1300, 70),
  ("tuolumne_mdw",   "File:Tuolumne Meadows - Daff Dome from Fairview Dome - 01 crop.jpg",1200,950,66),
  ("elcap",          "File:El Capitan, Yosemite, from base of southeast face.jpg", 900, 760, 66),
  ("merced",         "File:Yosemite National Park - 51684506854.jpg",           1200, 950, 66),
]

meta = {}
for key, title, fw, ow, q in WANT:
    r = api({"action":"query","format":"json","titles":title,"prop":"imageinfo",
             "iiprop":"url|extmetadata","iiurlwidth":str(fw),
             "iiextmetadatafilter":"LicenseShortName|LicenseUrl|Artist"})
    p = list(r["query"]["pages"].values())[0]
    if "imageinfo" not in p:
        print("MISS", key); continue
    ii = p["imageinfo"][0]; md = ii.get("extmetadata", {})
    raw = get(ii.get("thumburl") or ii["url"])
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.width > ow:
        im = im.resize((ow, round(im.height * ow / im.width)), Image.LANCZOS)
    dest = f"img/{key}.webp"
    im.save(dest, "WEBP", quality=q, method=6)
    meta[key] = {
      "artist": re.sub("<[^>]+>", "", (md.get("Artist") or {}).get("value","")).strip(),
      "license": (md.get("LicenseShortName") or {}).get("value",""),
      "licurl": (md.get("LicenseUrl") or {}).get("value",""),
      "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ","_")),
      "w": im.width, "h": im.height, "bytes": os.path.getsize(dest),
    }
    print(f"{key:17}{im.width}x{im.height}  {os.path.getsize(dest)//1024:4}KB  {meta[key]['license']:14}{meta[key]['artist'][:34]}")
    time.sleep(1.2)
json.dump(meta, open("img/meta.json","w"), ensure_ascii=False, indent=1)
print("TOTAL", sum(m["bytes"] for m in meta.values())//1024, "KB  -> base64 ~",
      int(sum(m["bytes"] for m in meta.values())*1.34)//1024, "KB")
