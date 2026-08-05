"""Inline every asset and emit the three things this page ships as.

  yosemite-westgate-1day.html  Japanese body fragment, for the Artifact host,
                               which supplies its own <head> and reset.
  standalone-ja.html           Japanese, complete document.
  standalone-en.html           English, complete document. This is the file
                               that gets handed to people, so it is the one
                               that has to survive being opened anywhere.

A complete document is not optional for a file someone opens directly: with
no charset the browser guesses and mangles the text, with no viewport it lays
out at 980px and renders zoomed out, and with no lang="ja" iOS picks a Chinese
face for the kanji.

Both languages share one stylesheet and one script — the English page is the
Japanese page's <style> and <script> with body.en.html spliced in between —
so a fix to either can't land in one language and miss the other.
"""
import base64, html, json, os, re, sys

JA = open("template.html", encoding="utf-8").read()
JA = re.sub(r"\n\s*--alpen-dim:[^\n]*", "", JA)

# CSS math functions require whitespace around + and -. Without it the whole
# declaration is invalid and silently dropped, and what the element falls back
# to then depends on the surrounding reset — so the page renders differently
# standalone than it does inside a host. Fail loudly instead.
bad = [m.group(0) for m in re.finditer(r"\b(?:clamp|calc|min|max)\([^;{}]*?\)", JA)
       if re.search(r"(?<=[\d%a-z])[+\-](?=[\d.])", m.group(0))]
assert not bad, "unspaced operator in CSS math function:\n  " + "\n  ".join(sorted(set(bad)))

meta = json.load(open("img/meta.json"))
d64 = lambda p, m: f"data:{m};base64," + base64.b64encode(open(p, "rb").read()).decode()

USED = ["hero_tunnelview","valleyview","bridalveil","merced","elcap","halfdome_gp",
        "taftpoint","gp_sunset","tenaya","sequoia","hetchhetchy","stars"]
NAMES = {"hero_tunnelview":"Tunnel View","valleyview":"Valley View / El Capitan",
 "bridalveil":"Bridalveil Fall","merced":"Merced River","elcap":"El Capitan",
 "halfdome_gp":"Half Dome from Glacier Point","taftpoint":"Taft Point",
 "gp_sunset":"Half Dome at sunset","tenaya":"Tenaya Lake",
 "sequoia":"Tuolumne Grove","hetchhetchy":"Hetch Hetchy Reservoir",
 "stars":"Yosemite night sky"}
CREDITS = "\n      ".join(
    f'<li>{html.escape(NAMES[k])} — {html.escape(meta[k]["artist"] or "Unknown")} / '
    f'{html.escape(meta[k]["license"])} ·<a href="{meta[k]["page"]}">Wikimedia Commons</a></li>'
    for k in USED)


def fill(text):
    text = re.sub(r"\{\{FONT:([a-z0-9\-]+)\}\}",
                  lambda m: "'" + d64(f"fonts/{m.group(1)}.woff2", "font/woff2") + "'", text)
    text = re.sub(r"\{\{IMG:([a-z0-9_]+)\}\}",
                  lambda m: d64(f"img/{m.group(1)}.webp", "image/webp"), text)
    text = text.replace("{{CREDITS}}", CREDITS)
    assert "{{" not in text, "unresolved placeholder: " + text[text.index("{{"):][:60]
    return text


# ── split the Japanese template into head / body / script ────────────────
TITLE_JA = re.search(r"<title>(.*?)</title>", JA, re.S).group(1)
head_end = JA.index("</style>") + len("</style>")
body_end = JA.index("<script>")
head_ja, body_ja, script = JA[:head_end], JA[head_end:body_end], JA[body_end:]
head_no_title = head_ja.replace(f"<title>{TITLE_JA}</title>", "", 1).lstrip()

body_en = open("body.en.html", encoding="utf-8").read()
TITLE_EN = "Yosemite in One Day — from the West Gate"

# ── the two bodies must stay structurally identical ──────────────────────
def shape(body, label):
    ids = sorted(set(re.findall(r'\bid="([^"]+)"', body)))
    return {
        "ids": ids,
        "checkboxes": body.count('<input type="checkbox">'),
        "radios": body.count('<input type="radio"'),
        "panels": len(re.findall(r'class="panel"', body)),
        "stops": len(re.findall(r'class="stop rv', body)),
        "reveals": len(re.findall(r'\brv\b', body)),
        "images": len(re.findall(r"\{\{IMG:", body)),
    }

sja, sen = shape(body_ja, "ja"), shape(body_en, "en")
drift = {k: (sja[k], sen[k]) for k in sja if sja[k] != sen[k]}
if drift:
    for k, (a, b) in drift.items():
        if k == "ids":
            print("  ids only in ja:", sorted(set(a) - set(b)), file=sys.stderr)
            print("  ids only in en:", sorted(set(b) - set(a)), file=sys.stderr)
        else:
            print(f"  {k}: ja={a} en={b}", file=sys.stderr)
    sys.exit("the two language bodies have drifted apart — see above")

CHECKS = sja["checkboxes"]
for lang, body in (("ja", body_ja), ("en", body_en)):
    n = int(re.search(r'id="cktotal">(\d+)<', body).group(1))
    assert n == CHECKS, f"{lang}: cktotal says {n}, there are {CHECKS} checkboxes"


def document(lang, title, head, body, desc):
    return (f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f"<title>{title}</title>\n"
            f'<meta name="description" content="{desc}">\n'
            '<meta name="color-scheme" content="dark">\n'
            '<meta name="theme-color" content="#080B10">\n'
            '<meta name="format-detection" content="telephone=no">\n'
            "<style>\nhtml{background:#080B10}\nbody{margin:0}\n</style>\n"
            f"{head}\n</head>\n<body>\n{body}\n{script}\n</body>\n</html>\n")


out = {
    "yosemite-westgate-1day.html": fill(JA),
    "standalone-ja.html": fill(document(
        "ja", TITLE_JA, head_no_title, body_ja,
        "Yosemite Westgate Lodge を拠点にヨセミテ国立公園を1日で回るプランと持ち物リスト。")),
    "standalone-en.html": fill(document(
        "en", TITLE_EN, head_no_title, body_en,
        "A one-day Yosemite plan and packing list, based out of Yosemite Westgate Lodge.")),
}
for name, text in out.items():
    open(name, "w", encoding="utf-8").write(text)
    print(f"built {name:32} {os.path.getsize(name)//1024:5} KB")

for name in ("standalone-ja.html", "standalone-en.html"):
    head = open(name, "rb").read(1024)
    assert b'<meta charset="utf-8">' in head, f"{name}: charset too late in the document"
    assert b"width=device-width" in head, f"{name}: viewport too late in the document"
print(f"heads OK · {CHECKS} checklist items in both languages · structures match")
