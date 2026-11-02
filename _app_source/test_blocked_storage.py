"""Simulate Android opening the file with storage blocked (SecurityError), on a Pixel profile. Old build vs new build."""
import pathlib, sys
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
NEW = (HERE.parent / "ML_Security_Course_App.html").as_uri()
OLD_PATH = HERE / "old_build.html"   # optional: a copy made before the storage fix
CASES = [("new build", NEW, True)]
if OLD_PATH.exists():
    CASES.insert(0, ("old build", OLD_PATH.as_uri(), False))
BLOCK = "Object.defineProperty(window,'localStorage',{configurable:true,get(){throw new DOMException('The operation is insecure.','SecurityError')}});"
fails = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for label, url, expect_ok in CASES:
        ctx = b.new_context(**p.devices["Pixel 7"], offline=True)
        ctx.add_init_script(BLOCK)
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(300)
        cards = pg.locator("#course .card").count()
        works = cards >= 8 and not errs
        print(f"{label}: module cards={cards}, page errors={errs[:1]} -> {'WORKS' if works else 'BROKEN'}")
        if label == "new build":
            banner = pg.get_by_text("Progress can't be saved automatically").count()
            pg.locator("#course .modhead").first.click()
            pg.locator('input[data-sec="1Learn"]').check()
            q = pg.locator("#q1"); q.get_by_text("Reveal answer").click()
            pg.get_by_role("link", name="Flashcards").click(); pg.locator("#fc").click()
            pg.get_by_role("link", name="Library (237)").click()
            lib = pg.locator("#llist .lib-row").count()
            pg.get_by_role("link", name="Progress & backup").click()
            with pg.expect_download() as dl:
                pg.locator("#ex").click()
            exported = '"1Learn": true' in pathlib.Path(dl.value.path()).read_text()
            print(f"  banner shown={banner == 1}, ticks/reveal/flashcards work, library rows={lib}, export has the tick={exported}, errors={errs[:1]}")
            pg.screenshot(path=str(HERE / "shots" / "shot_pixel_blocked.png"))
            ok = works and banner == 1 and lib == 237 and exported and not errs
        else:
            ok = (works == expect_ok)
        fails += not ok
        ctx.close()
    b.close()
print("RESULT:", "as expected" if fails == 0 else f"{fails} unexpected")
sys.exit(fails)
