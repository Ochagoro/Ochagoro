"""Insert Waze / Google Maps handoff links next to every destination.

Every destination carries its own coordinate, from geo.json (OSM via Overpass,
plus Nominatim for one street address). Never a ?q= name search: resolving a
name needs connectivity, and there is none in the park, which is exactly where
someone would be tapping these. Nothing is guessed — a pin that is confidently
wrong in the Sierra is the failure mode worth designing against.
"""
import io, json, urllib.parse

GEO = json.load(open("geo.json"))

def go(key=None, search=None, lang="ja"):
    waze_label, maps_label = "Waze", "Maps"
    if key:
        g = GEO[key]
        ll = f'{g["lat"]},{g["lon"]}'
        waze = f"https://waze.com/ul?ll={ll}&navigate=yes"
        maps = f"https://www.google.com/maps/search/?api=1&query={ll}"
        coord = f'<span class="coord">{g["lat"]}, {g["lon"]}</span>'
    else:
        q = urllib.parse.quote(search)
        waze = f"https://waze.com/ul?q={q}&navigate=yes"
        maps = f"https://www.google.com/maps/search/?api=1&query={q}"
        coord = f'<span class="coord">{"名前で検索" if lang == "ja" else "by name"}</span>'
    return (f'<span class="go"><a class="waze" href="{waze}">{waze_label}</a>'
            f'<a href="{maps}">{maps_label}</a>{coord}</span>')

# ── directory entries, in document order ────────────────────────────────
DIR = [
    ("Backwoods Burgers",            dict(key="backwoods")),
    (None,                           None),   # "fill up in Oakdale" — not one place
    ("Mar-Val Food Stores",          dict(key="marval")),
    ("Iron Door Saloon",             dict(key="irondoor")),
    ("Rainbow Pool Day Use Area",    dict(key="rainbowpool")),
    ("Yosemite Westgate Lodge",      dict(key="lodge")),
    ("Lucky Buck Cafe",              dict(key="luckybuck")),
    ("Crane Flat Gas Station",       dict(key="craneflat")),
    ("Village Store",                dict(key="villagestore")),
    ("Degnan's Kitchen",             dict(key="degnans")),
    ("Base Camp Eatery",             dict(key="valleylodge")),
    ("Village Grill",                dict(key="villagegrill")),
    ("Curry Village Pizza Deck",     dict(key="curry")),
    ("Glacier Point Gift Shop",      dict(key="glacierpt")),
]

# ── explicit anchors elsewhere in the page: (unique substring, insert-after, spec)
def anchors(lang):
    L = lang == "ja"
    A = []

    def corridor(nameframe, spec):
        """Corridor rows: the links go inside the name cell as a third line."""
        A.append((nameframe, spec))

    # drive-day corridor
    corridor('<span>1214 W F St, Oakdale ／ <b>出発時に給油を済ませる</b></span>' if L
             else '<span>1214 W F St, Oakdale — <b>fill the tank before leaving</b></span>',
             dict(key="backwoods"))
    corridor('<span>19000 Main St, Groveland ／ 明日の食料・水・氷。30分</span>' if L
             else "<span>19000 Main St, Groveland — tomorrow's food, water, ice. 30 min</span>",
             dict(key="marval"))
    corridor('<span>Groveland から東へ15マイル · $10／台・40分</span>' if L
             else '<span>15 mi east of Groveland · $10 per car · 40 min</span>',
             dict(key="rainbowpool"))
    corridor('<span>チェックイン開始ちょうど。荷物を降ろして25分</span>' if L
             else '<span>exactly when check-in opens. Drop the bags, 25 min</span>',
             dict(key="lodge"))

    # base-section corridor (distances from the lodge)
    corridor('<span>Stanislaus NF · トイレあり</span>' if L
             else '<span>Stanislaus NF · restrooms</span>', dict(key="rimworld"))
    corridor('<span>Tioga Rd 分岐 · 園内ガソリンスタンド</span>' if L
             else '<span>Tioga Rd junction · in-park gas</span>', dict(key="craneflat"))
    corridor('<span>Tioga Rd · 標高 2,484m</span>' if L
             else '<span>Tioga Rd · 8,150 ft</span>', dict(key="tenaya"))
    corridor('<span>標高 2,199m · 渓谷経由</span>' if L
             else '<span>7,214 ft · via the valley</span>', dict(key="glacierpt"))

    # main-day timeline: after the chips row of each driving destination
    A += [
        ('<div class="chips"><span class="acc">$35 / vehicle</span><span>cards accepted</span><span>4,900 ft</span></div>' if not L
         else '<div class="chips"><span class="acc">$35 / vehicle</span><span>カード可</span><span>標高 約1,490m</span></div>',
         dict(key="bigoakflat")),
        ('<figcaption><span>Valley View / Merced River</span><span>4,000 ft</span></figcaption>' if not L
         else '<figcaption><span>Valley View / Merced River</span><span>1,200 m</span></figcaption>',
         dict(key="valleyview")),
        ('<div class="chips"><span>Wawona Rd (Hwy 41)</span><span>restrooms</span><span>10 min uphill from the valley</span></div>' if not L
         else '<div class="chips"><span>Wawona Rd (Hwy 41)</span><span>トイレあり</span><span>渓谷から車で10分の登り</span></div>',
         dict(key="tunnelview")),
        ('<figcaption><span>Bridalveil Fall · 620 ft</span><span>0.5 mi round trip, paved</span></figcaption>' if not L
         else '<figcaption><span>Bridalveil Fall · 189 m</span><span>往復 0.8 km / 舗装路</span></figcaption>',
         dict(key="bridalveil")),
        ('<span class="acc">free shuttle, summer, morning to night</span><span>bike rental too</span><span>water refill here</span></div>' if not L
         else '<span class="acc">無料シャトル 夏季 朝〜夜</span><span>レンタサイクルもあり</span><span>給水所あり</span></div>',
         dict(key="villagestore")),
        ('<figcaption><span>Merced River · Yosemite Valley</span><span>start at Happy Isles</span></figcaption>' if not L
         else '<figcaption><span>Merced River · Yosemite Valley</span><span>Happy Isles 起点</span></figcaption>',
         dict(key="happyisles")),
        ('<h3>Picnic on the sand at Swinging Bridge</h3>' if not L
         else '<h3>Swinging Bridge の河原でピクニック</h3>', dict(key="swinging")),
        ('<span>store 9:30–17:00</span><span>mid-50s°F by evening</span></div>' if not L
         else '<span>売店は 9:30–17:00</span><span>夕方は 12〜16℃</span></div>',
         dict(key="glacierpt")),
        ('<figcaption><span>Taft Point · 7,503 ft</span><span>the Fissures, and no railings</span></figcaption>' if not L
         else '<figcaption><span>Taft Point · 2,286 m</span><span>柵のない裂け目（Fissures）</span></figcaption>',
         dict(key="taftpoint")),
        ('<div class="chips"><span>trailheads off Glacier Point Rd</span><span>headlamp required</span></div>' if not L
         else '<div class="chips"><span>トレイル入口は Glacier Point Rd 沿い</span><span>ヘッドランプ必携</span></div>',
         dict(key="sentineldome")),
    ]
    return A


def apply(path, lang):
    s = io.open(path, encoding="utf-8").read()
    n = 0

    # directory: insert after the .card paragraph that follows each shop name
    for name, spec in DIR:
        if name is None or spec is None:
            continue
        i = s.index(f'<p class="shopname">{name}')
        j = s.index('</p>', s.index('<p class="card">', i)) + len('</p>')
        s = s[:j] + "\n            " + go(lang=lang, **spec) + s[j:]
        n += 1

    for frame, spec in anchors(lang):
        assert frame in s, f"{path}: anchor missing -> {frame[:60]}"
        assert s.count(frame) == 1, f"{path}: anchor x{s.count(frame)} -> {frame[:50]}"
        s = s.replace(frame, frame + go(lang=lang, **spec))
        n += 1

    io.open(path, "w", encoding="utf-8").write(s)
    print(f"{path}: inserted {n} link rows")


apply("template.html", "ja")
apply("body.en.html", "en")
