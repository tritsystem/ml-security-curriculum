"""Drive-preview conditions: JavaScript disabled, Pixel profile. Content must be readable."""
import pathlib, sys
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent
URL = (HERE.parent / "ML_Security_Course_App.html").as_uri()
fails = []
def ok(c, m): print(("PASS " if c else "FAIL ") + m); (None if c else fails.append(m))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(**p.devices["Pixel 7"], java_script_enabled=False, offline=True).new_page()
    pg.goto(URL)
    ok(pg.locator("#course .card .modhead").count() == 8, "8 modules visible without JavaScript")
    ok(pg.get_by_text("Who controls the input?").is_visible(), "module text is readable")
    ok(pg.get_by_text("read-only version").is_visible(), "read-only explanation shown")
    first = pg.locator("#course details").first
    ok(not first.locator(".ans-static").is_visible(), "answer hidden until tapped")
    first.locator("summary").click()
    ok(first.locator(".ans-static").is_visible(), "tap 'Reveal answer' shows it (no JS)")
    ok(pg.locator("#course details").count() == 16, "all 16 questions have reveal-able answers")
    ok(pg.locator("#lib .lib-row").count() == 237, "library: 237 items rendered statically")
    ok(pg.locator("#lib a[href^='https://']").count() >= 250, "library links present")
    pg.get_by_role("link", name="Library (237)").click()
    ok("#lib" in pg.url, "Library tab jumps to the library without JS")
    ok(pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), "no sideways scrolling on Pixel width")
    pg.goto(URL); pg.screenshot(path=str(HERE / "shots" / "shot_nojs.png"))
    b.close()
print(f"{len(fails)} failed"); sys.exit(len(fails))
