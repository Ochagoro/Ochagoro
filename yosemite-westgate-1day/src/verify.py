"""Prove the two builds render identically.

The page ships twice: as a complete document (index.html) and as a body
fragment that a host wraps in its own <head> and reset (artifact-fragment.html).
Any property left at a browser default renders one way standalone and another
way inside the host — a silently dropped declaration is the usual cause, since
what an element falls back to is exactly what the reset decides.

So: wrap the fragment in a deliberately aggressive reset, then compare the two
against each other. Element boxes first (tells you *what* moved), pixels second
(catches weight and color drift that boxes miss). Both must come out clean.

    python3 build.py && python3 verify.py

Requires: playwright, Pillow.
"""
import glob, pathlib, sys
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

CHROME = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
EXE = CHROME[-1] if CHROME else None
SECTIONS = ["hero", "drive", "base", "profile", "day", "alts", "pack", "eve", "rules"]
VIEWPORTS = [("mobile", {"width": 390, "height": 844}), ("desk", {"width": 1280, "height": 900})]

HOST_RESET = """*,*::before,*::after{box-sizing:border-box;border:0 solid}
html{line-height:1.5;-webkit-text-size-adjust:100%;font-family:ui-sans-serif,system-ui,sans-serif}
body{margin:0;line-height:inherit}
h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit;margin:0}
p,figure,blockquote,dl,dd,ol,ul,pre,hr{margin:0}
ol,ul{list-style:none;padding:0}
button,input,select,textarea{font-family:inherit;font-size:100%;font-weight:inherit;
  line-height:inherit;color:inherit;margin:0;padding:0}
button{background:transparent;background-image:none;text-transform:none;cursor:pointer}
img,svg,video,canvas{display:block;vertical-align:middle;max-width:100%;height:auto}
a{color:inherit;text-decoration:inherit}"""

PROBE = """() => {
  const out = {};
  document.querySelectorAll('section,header,footer,nav,h1,h2,h3,p,dl,dd,ul,li,button,figure,'
    + '.h2,.lede,.eyebrow,.vitals,.corridor,.facts,.chart,.tl,.stop,.tabs,.panel,.banner,'
    + '.mini,.verdict,.packhead,.ring,.reset,.kits,.kit,.kit label,.eve-grid,.rules,.rule,'
    + '.disclaim,#credits').forEach((el, i) => {
      const r = el.getBoundingClientRect();
      out[i + ':' + el.tagName.toLowerCase() + '.' + (el.className || '').toString().slice(0, 26)]
        = [Math.round(r.width), Math.round(r.height)];
    });
  out.__PAGE__ = [document.documentElement.clientWidth, document.body.scrollHeight];
  return out;
}"""


def make_hosted(fragment="yosemite-westgate-1day.html", out="hosted.html"):
    frag = open(fragment, encoding="utf-8").read()
    title = frag.split("<title>")[1].split("</title>")[0]
    body = frag.replace(f"<title>{title}</title>", "", 1).lstrip()
    open(out, "w", encoding="utf-8").write(
        '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title}</title>\n<style>{HOST_RESET}</style>\n</head>\n"
        f"<body>\n{body}\n</body>\n</html>\n")
    return out


def capture(page_file, tag, vp):
    """Element boxes plus one screenshot per section, with animations frozen."""
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE, args=["--no-sandbox"])
        ctx = b.new_context(viewport=vp, device_scale_factor=1, locale="ja-JP",
                            is_mobile=vp["width"] < 600, has_touch=vp["width"] < 600,
                            reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto("file://" + str(pathlib.Path(page_file).resolve()), wait_until="load")
        pg.wait_for_timeout(1200)
        boxes = pg.evaluate(PROBE)
        for y in range(0, pg.evaluate("document.body.scrollHeight"), 300):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(35)
        pg.wait_for_timeout(800)
        shots = {}
        for s in SECTIONS:
            pg.evaluate("scrollTo(0,0)" if s == "hero"
                        else f"document.getElementById('{s}').scrollIntoView()")
            pg.wait_for_timeout(420)
            shots[s] = f"cmp-{tag}-{s}.png"
            pg.screenshot(path=shots[s])
        b.close()
    return boxes, shots


def main():
    if not EXE:
        sys.exit("no chromium found under /opt/pw-browsers")
    make_hosted()
    failures = 0
    for name, vp in VIEWPORTS:
        print(f"\n=== {name} {vp['width']}x{vp['height']} ===")
        ab, ash = capture("standalone.html", f"{name}-standalone", vp)
        bb, bsh = capture("hosted.html", f"{name}-hosted", vp)

        moved = [k for k in ab if k in bb and ab[k] != bb[k]]
        print(f"  page {ab['__PAGE__']} vs {bb['__PAGE__']}")
        for k in moved[:20]:
            print(f"    BOX {k:50} {ab[k]} vs {bb[k]}")
        print(f"  boxes differing: {len(moved)}")
        failures += len(moved)

        dirty = []
        for s in SECTIONS:
            a = Image.open(ash[s]).convert("RGB")
            b = Image.open(bsh[s]).convert("RGB")
            if a.size != b.size:
                dirty.append(f"{s} size {a.size} vs {b.size}")
                continue
            bbox = ImageChops.difference(a, b).getbbox()
            if bbox:
                dirty.append(f"{s} at {bbox}")
        for d in dirty:
            print("    PIX", d)
        print("  pixels: clean" if not dirty else f"  pixels: {len(dirty)} section(s) differ")
        failures += len(dirty)

    print("\nOK — the two builds render identically." if not failures
          else f"\nFAILED — {failures} difference(s).")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
