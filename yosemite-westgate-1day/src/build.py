import base64, html, json, os, re
src = open("template.html", encoding="utf-8").read()
src = re.sub(r"\n\s*--alpen-dim:[^\n]*", "", src)
meta = json.load(open("img/meta.json"))
d64 = lambda p, m: f"data:{m};base64," + base64.b64encode(open(p,"rb").read()).decode()
src = re.sub(r"\{\{FONT:([a-z0-9\-]+)\}\}", lambda m: "'"+d64(f"fonts/{m.group(1)}.woff2","font/woff2")+"'", src)
src = re.sub(r"\{\{IMG:([a-z0-9_]+)\}\}", lambda m: d64(f"img/{m.group(1)}.webp","image/webp"), src)
USED=["hero_tunnelview","valleyview","bridalveil","merced","elcap","halfdome_gp",
      "taftpoint","gp_sunset","tenaya","sequoia","stars"]
NAMES={"hero_tunnelview":"Tunnel View","valleyview":"Valley View / El Capitan",
 "bridalveil":"Bridalveil Fall","merced":"Merced River","elcap":"El Capitan",
 "halfdome_gp":"Half Dome from Glacier Point","taftpoint":"Taft Point",
 "gp_sunset":"Half Dome at sunset","tenaya":"Tenaya Lake",
 "sequoia":"Tuolumne Grove","stars":"Yosemite night sky"}
rows=[f'<li>{html.escape(NAMES[k])} — {html.escape(meta[k]["artist"] or "Unknown")} / '
      f'{html.escape(meta[k]["license"])} ·<a href="{meta[k]["page"]}">Wikimedia Commons</a></li>' for k in USED]
src = src.replace("{{CREDITS}}", "\n      ".join(rows))
assert "{{" not in src
open("yosemite-westgate-1day.html","w",encoding="utf-8").write(src)
print("built", os.path.getsize("yosemite-westgate-1day.html")//1024, "KB")
