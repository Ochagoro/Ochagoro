"""Inline every asset into the page.

Two outputs, because they are consumed differently:

  yosemite-westgate-1day.html  — body fragment for the Artifact host, which
                                 supplies its own <head> (charset, viewport).
  standalone.html              — a complete document for opening the file
                                 directly on a phone. Without an explicit
                                 charset the browser guesses and mangles the
                                 Japanese; without a viewport it lays the page
                                 out at 980px and zooms out; without lang="ja"
                                 iOS renders the kanji in a Chinese face.
"""
import base64, html, json, os, re

src = open("template.html", encoding="utf-8").read()
src = re.sub(r"\n\s*--alpen-dim:[^\n]*", "", src)
meta = json.load(open("img/meta.json"))
d64 = lambda p, m: f"data:{m};base64," + base64.b64encode(open(p, "rb").read()).decode()

src = re.sub(r"\{\{FONT:([a-z0-9\-]+)\}\}",
             lambda m: "'" + d64(f"fonts/{m.group(1)}.woff2", "font/woff2") + "'", src)
src = re.sub(r"\{\{IMG:([a-z0-9_]+)\}\}",
             lambda m: d64(f"img/{m.group(1)}.webp", "image/webp"), src)

USED = ["hero_tunnelview","valleyview","bridalveil","merced","elcap","halfdome_gp",
        "taftpoint","gp_sunset","tenaya","sequoia","stars"]
NAMES = {"hero_tunnelview":"Tunnel View","valleyview":"Valley View / El Capitan",
 "bridalveil":"Bridalveil Fall","merced":"Merced River","elcap":"El Capitan",
 "halfdome_gp":"Half Dome from Glacier Point","taftpoint":"Taft Point",
 "gp_sunset":"Half Dome at sunset","tenaya":"Tenaya Lake",
 "sequoia":"Tuolumne Grove","stars":"Yosemite night sky"}
rows = [f'<li>{html.escape(NAMES[k])} — {html.escape(meta[k]["artist"] or "Unknown")} / '
        f'{html.escape(meta[k]["license"])} ·<a href="{meta[k]["page"]}">Wikimedia Commons</a></li>'
        for k in USED]
src = src.replace("{{CREDITS}}", "\n      ".join(rows))
assert "{{" not in src

open("yosemite-westgate-1day.html", "w", encoding="utf-8").write(src)

# ── standalone: lift the <title> into a real <head> ────────────────────────
title = re.search(r"<title>(.*?)</title>", src, re.S).group(1)
body = src.replace(f"<title>{title}</title>", "", 1).lstrip()

standalone = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Yosemite Westgate Lodge を拠点にヨセミテ国立公園を1日で回るプランと持ち物リスト。">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#080B10">
<meta name="format-detection" content="telephone=no">
<style>
html{{background:#080B10}}
body{{margin:0}}
</style>
</head>
<body>
{body}
</body>
</html>
"""
open("standalone.html", "w", encoding="utf-8").write(standalone)

for f in ("yosemite-westgate-1day.html", "standalone.html"):
    print(f"built {f}  {os.path.getsize(f)//1024} KB")

# charset must land inside the first 1024 bytes or browsers stop looking
head = open("standalone.html", "rb").read(1024)
assert b'<meta charset="utf-8">' in head, "charset too late in the document"
assert b"width=device-width" in head, "viewport too late in the document"
print("standalone head OK (charset + viewport within first 1024 bytes)")
