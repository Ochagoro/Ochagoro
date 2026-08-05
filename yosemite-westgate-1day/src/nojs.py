import glob, pathlib
from playwright.sync_api import sync_playwright
exe=sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))[-1]
URL="file://"+str(pathlib.Path("standalone-en.html").resolve())
PANELS="""() => [...document.querySelectorAll('.panel')]
  .map(p=>p.id+'='+(getComputedStyle(p).display==='none'?'hidden':'SHOWN')).join(' ')"""
def run(label, js):
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=exe,args=["--no-sandbox"])
        ctx=b.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True,
                          locale="ja-JP",java_script_enabled=js)
        pg=ctx.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(URL,wait_until="load"); pg.wait_for_timeout(1400)
        print(f"\n--- {label} ---")
        print(" panels:", pg.evaluate(PANELS) if js else "(need js to read; using CSS check below)")
        # works with JS off too: read via attribute-free CSS state by clicking labels
        print(" counter:", pg.locator("#ckdone").inner_text(), "/", pg.locator("#cktotal").inner_text())
        print(" reset visible:", pg.locator("#reset").is_visible())
        print(" noscript note visible:", pg.locator(".nojs").is_visible() if pg.locator(".nojs").count() else "n/a")
        # switch to the other plans by clicking their labels
        for lab, want in [('label[for="pk-d2"]',"p-d2"), ('label[for="pk-d3"]',"p-d3"),
                          ('label[for="pk-c"]',"p-c")]:
            pg.click(lab); pg.wait_for_timeout(250)
            shown = pg.locator("#"+want).is_visible()
            print(f" click {lab:24} -> #{want} visible={shown}")
        # tick three boxes and confirm the tick renders
        labs=pg.locator(".kit label")
        for i in (0,1,2): labs.nth(i).click()
        pg.wait_for_timeout(250)
        print(" ticks rendered:", pg.evaluate("""[...document.querySelectorAll('.kit input')]
   .filter(c=>getComputedStyle(c.nextElementSibling).backgroundColor!=='rgba(0, 0, 0, 0)').length""") if js else "(JS off: read from screenshot)")
        print(" counter after:", pg.locator("#ckdone").inner_text(), "/", pg.locator("#cktotal").inner_text())
        print(" errors:", errs or "none")
        pg.screenshot(path=f"nojs-{'on' if js else 'off'}.png")
        b.close()
run("JS ENABLED", True)
run("JS DISABLED", False)
