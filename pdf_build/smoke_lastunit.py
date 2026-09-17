# -*- coding: utf-8 -*-
"""Smoke test: first visit lands on Unità 1; revisit restores the last unit."""
import os, pathlib, sys
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(r"D:\意大利语材料\实用意大利语会话\index.html").as_uri()
errors = []

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="msedge")
    except Exception:
        for exe in (
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ):
            if os.path.exists(exe):
                browser = p.chromium.launch(executable_path=exe)
                break
        else:
            raise
    ctx = browser.new_context()
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    # ---- visit 1: should land on c1u1 ----
    page.goto(PAGE)
    page.wait_for_timeout(600)
    welcome_visible = page.eval_on_selector("#welcomePanel", "el=>getComputedStyle(el).display")
    heading = page.inner_text(".unit-content h2")
    active = page.eval_on_selector(".unit-item.active", "el=>el.dataset.uid")
    stored = page.evaluate("localStorage.getItem('ital_conv_last_unit')")
    print("visit1 | welcome display =", welcome_visible)
    print("visit1 | heading        =", heading.strip())
    print("visit1 | active uid     =", active)
    print("visit1 | localStorage   =", stored)

    # ---- click a later unit (c3u4) ----
    page.click('.unit-item[data-uid="c3u4"]')
    page.wait_for_timeout(400)
    stored2 = page.evaluate("localStorage.getItem('ital_conv_last_unit')")
    print("after click c3u4 | localStorage =", stored2)

    # ---- visit 2 (same context = same localStorage): should restore c3u4 ----
    page2 = ctx.new_page()
    page2.on("pageerror", lambda e: errors.append(str(e)))
    page2.goto(PAGE)
    page2.wait_for_timeout(600)
    heading2 = page2.inner_text(".unit-content h2")
    active2 = page2.eval_on_selector(".unit-item.active", "el=>el.dataset.uid")
    print("visit2 | heading    =", heading2.strip())
    print("visit2 | active uid =", active2)

    # ---- visit 3 in a FRESH context (no localStorage): should fall back to c1u1 ----
    ctx2 = browser.new_context()
    page3 = ctx2.new_page()
    page3.on("pageerror", lambda e: errors.append(str(e)))
    page3.goto(PAGE)
    page3.wait_for_timeout(600)
    heading3 = page3.inner_text(".unit-content h2")
    print("fresh  | heading    =", heading3.strip())

    browser.close()

print("console/page errors:", errors if errors else "none")
ok = (
    welcome_visible == "none"
    and "AFFITTARE UNA CASA" in heading
    and active == "c1u1"
    and stored == "c1u1"
    and stored2 == "c3u4"
    and active2 == "c3u4"
    and "AEROPORTO" in heading2
    and "AFFITTARE UNA CASA" in heading3
    and not errors
)
print("SMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
