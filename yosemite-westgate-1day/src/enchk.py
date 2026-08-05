"""Smoke-test the English standalone at three widths."""
import glob, pathlib
from playwright.sync_api import sync_playwright

exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))[-1]
URL = "file://" + str(pathlib.Path("standalone-en.html").resolve())
HIDDEN = ("[...document.querySelectorAll('.rv')]"
          ".filter(e=>parseFloat(getComputedStyle(e).opacity)<0.9).length")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
    for w, h, mob in [(390, 844, True), (768, 1024, True), (1280, 900, False)]:
        ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=mob,
                            has_touch=mob, locale="en-US")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1300)
        for y in range(0, pg.evaluate("document.body.scrollHeight"), 350):
            pg.evaluate(f"scrollTo(0,{y})")
            pg.wait_for_timeout(40)
        pg.wait_for_timeout(900)
        print(f"{w}x{h}  lang={pg.evaluate('document.documentElement.lang')}"
              f"  charset={pg.evaluate('document.characterSet')}"
              f"  layoutW={pg.evaluate('document.documentElement.clientWidth')}"
              f"  h-overflow={pg.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')}"
              f"  still-hidden={pg.evaluate(HIDDEN)}"
              f"  errors={errs or 'none'}")
        if w == 390:
            for sec in ["drive", "day", "shops", "pack", "alts"]:
                pg.evaluate(f"document.getElementById('{sec}').scrollIntoView()")
                pg.wait_for_timeout(550)
                pg.screenshot(path=f"en-{sec}.png")
        ctx.close()
    b.close()
