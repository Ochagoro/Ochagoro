import glob, pathlib
from playwright.sync_api import sync_playwright
exe = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))[-1]
URL = "file://" + str(pathlib.Path("standalone.html").resolve())
COUNT = """() => {
  const els=[...document.querySelectorAll('.rv')];
  const hidden=els.filter(e=>parseFloat(getComputedStyle(e).opacity)<0.9);
  return [els.length, hidden.length];
}"""

def run(label, *, js=True, kill_io=False, stub_io=False, wait=1500):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
        ctx = b.new_context(viewport={"width":390,"height":844}, is_mobile=True,
                            has_touch=True, locale="ja-JP", java_script_enabled=js)
        pg = ctx.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        if kill_io:
            pg.add_init_script("delete window.IntersectionObserver;")
        if stub_io:
            # observer constructs fine but never delivers a callback
            pg.add_init_script("window.IntersectionObserver=function(){"
                               "this.observe=function(){};this.unobserve=function(){};"
                               "this.disconnect=function(){};};")
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(wait)
        total, hidden = pg.evaluate(COUNT)
        # is the last section actually painted?
        tail = pg.evaluate("""() => {
          const f=document.querySelector('footer'); const r=f.getBoundingClientRect();
          return [Math.round(r.height), getComputedStyle(f).opacity];
        }""")
        print(f"{label:34} .rv total={total:3} hidden={hidden:3}  footer h={tail[0]}  errors={errs or 'none'}")
        b.close()

run("normal (scrolled to top)")
run("JS disabled", js=False)
run("no IntersectionObserver", kill_io=True)
run("IO never fires, +1.5s", stub_io=True, wait=1500)
run("IO never fires, +3.5s failsafe", stub_io=True, wait=3600)
