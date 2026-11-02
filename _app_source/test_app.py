"""End-to-end test of the study app in headless Chromium, offline."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright
APP = (pathlib.Path(__file__).resolve().parent.parent / "ML_Security_Course_App.html").as_uri()
SHOTS = pathlib.Path(__file__).resolve().parent / "shots"
errors, fails = [], []
def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond: fails.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(offline=True, accept_downloads=True, viewport={"width": 1100, "height": 900})
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(APP)
    ok(pg.locator("#course .card").count() == 8, "8 module cards render offline")
    pg.locator("#course .modhead").first.click()
    ok(pg.locator("#course .modbody").first.is_visible(), "module 1 expands")
    ok(pg.locator("#course .modbody").first.locator("a[target=_blank]").count() >= 2, "module 1 has external links opening in new tab")
    pg.locator('input[data-sec="1Learn"]').check()
    ok("1/4" in pg.locator("#mp1").inner_text(), "ticking Learn updates module progress to 1/4")
    ok(pg.evaluate("parseFloat(document.querySelector('#topbar').style.width)") > 0, "top progress bar moves")
    q1 = pg.locator("#q1")
    ok(not q1.locator(".a").is_visible(), "answer 1 hidden before reveal")
    q1.get_by_text("Reveal answer").click()
    ok(q1.locator(".a").is_visible(), "answer 1 visible after reveal")
    q1.get_by_text("I knew it").click()
    ok("knew it" in q1.locator("[data-qs]").inner_text(), "grading records 'knew it'")
    pg.locator('textarea[data-note="1"]').fill("pickle = RCE; test the planted bug first")
    pg.locator('[data-tm="1"]').click(); pg.wait_for_timeout(2300); pg.locator('[data-tm="1"]').click()
    ok(pg.locator("#t1").inner_text() >= "00:02", f"timer counts (shows {pg.locator('#t1').inner_text()})")
    pg.screenshot(path=str(SHOTS / "shot_course.png"), full_page=False)

    pg.get_by_role("link", name="Flashcards").click()
    ok(pg.locator("#fc").is_visible(), "flashcard renders")
    pg.locator("#fc").click(); ok(pg.locator("#fc .ans").is_visible(), "flashcard flips to answer")
    pg.locator("#fn").click(); ok(pg.locator("#fc").is_visible(), "missed-it moves to next card")
    pg.screenshot(path=str(SHOTS / "shot_cards.png"))

    pg.get_by_role("link", name="Library (237)").click()
    total = pg.locator("#llist .lib-row").count(); ok(total == 237, f"library lists 237 items (got {total})")
    pg.locator("#ls").fill("safetensors")
    n = pg.locator("#llist .lib-row").count(); ok(1 <= n <= 6, f"search 'safetensors' narrows the list ({n} rows)")
    pg.locator("#llist input[data-lib]").first.check()
    ok("done 1/237" in pg.locator("#lsum").inner_text(), "ticking a library item updates the tally")
    pg.locator("#ls").fill(""); pg.select_option("#lp", label="Vol II · L. Conference proceedings (the research frontier)")
    ok(pg.locator("#llist .lib-row").count() == 10, "part filter shows Vol II part L (10 items)")
    pg.screenshot(path=str(SHOTS / "shot_lib.png"))

    pg.get_by_role("link", name="Progress & backup").click()
    ok("1/16" in pg.locator("#prog").inner_text() or "1/16" in pg.content(), "progress page shows 1/16 questions known")
    with pg.expect_download() as dl:
        pg.locator("#ex").click()
    exp = json.loads(pathlib.Path(dl.value.path()).read_text())
    ok(exp["sec"].get("1Learn") is True and exp["q"].get("1") == "ok" and "pickle" in exp["notes"].get("1", ""), "export contains ticks, grades and notes")
    pg.screenshot(path=str(SHOTS / "shot_prog.png"))

    pg.reload()
    ok(pg.locator('input[data-sec="1Learn"]').is_checked(), "tick persists across reload")
    ok("pickle" in pg.locator('textarea[data-note="1"]').input_value(), "note persists across reload")

    pg2 = ctx.browser.new_context(offline=True).new_page(); pg2.goto(APP)
    pg2.get_by_role("link", name="Progress & backup").click()
    pg2.locator("#im").set_input_files(dl.value.path())
    pg2.wait_for_timeout(300)
    ok(pg2.evaluate("JSON.parse(localStorage.getItem('mlsec_course_v1')).notes['1']").startswith("pickle"), "import restores progress in a fresh browser")

    mob = b.new_context(offline=True, viewport={"width": 390, "height": 844}, is_mobile=True).new_page(); mob.goto(APP)
    ok(mob.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), "no horizontal scroll on phone width")
    mob.screenshot(path=str(SHOTS / "shot_mobile.png"))
    b.close()

real_errors = [e for e in errors if "net::ERR_INTERNET_DISCONNECTED" not in e]
ok(not real_errors, f"no JavaScript errors ({real_errors[:3]})")
print(f"\n{len(fails)} failed")
sys.exit(1 if fails else 0)
