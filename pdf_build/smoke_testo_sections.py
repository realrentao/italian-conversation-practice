# -*- coding: utf-8 -*-
"""Smoke test: video-text segments are promoted to top-level sections."""
import pathlib, sys
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(r"D:\意大利语材料\实用意大利语会话\index.html").as_uri()
errors = []


def titles(page):
    return page.eval_on_selector_all(".section-title", "els=>els.map(e=>e.innerText.trim())")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    # ---- c1u1: 4 segments ----
    page.goto(PAGE)
    page.click('.unit-item[data-uid="c1u1"]')
    page.wait_for_timeout(400)
    t1 = titles(page)
    segs = page.eval_on_selector_all(".dialogue-seg", "els=>els.length")
    print("c1u1 titles:", t1)
    print("c1u1 dialogue-seg count:", segs)

    # ---- c5u4: only 1 segment -> no numbering ----
    page.click('.unit-item[data-uid="c5u4"]')
    page.wait_for_timeout(400)
    t2 = titles(page)
    print("c5u4 titles:", t2)

    # ---- play button still wired ----
    page.click('.unit-item[data-uid="c1u1"]')
    page.wait_for_timeout(300)
    onclick = page.eval_on_selector(".dialogue-seg .d-play", "el=>el.getAttribute('onclick')")
    print("first seg play onclick:", onclick)

    browser.close()

print("errors:", errors if errors else "none")
ok = (
    segs == 4
    and not any(t == "Testo 视频文本" for t in t1)
    and all(any(f"视频文本 {i}" in t for t in t1) for i in range(1, 5))
    and all(any(f"Testo {i}" in t for t in t1) for i in range(1, 5))
    and any("视频文本" in t and not any(ch.isdigit() for ch in t) for t in t2)
    and "playDialogue(this,'c1u1',0)" in onclick
    and not errors
)
print("SMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
