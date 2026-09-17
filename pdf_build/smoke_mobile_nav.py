# -*- coding: utf-8 -*-
"""Smoke test: on mobile, picking a unit auto-collapses the sidebar."""
import os, pathlib, sys
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(r"D:\意大利语材料\实用意大利语会话\index.html").as_uri()
errors = []


def state(page):
    return page.evaluate(
        """() => ({
            open: document.getElementById('sidebar').classList.contains('open'),
            overlay: document.getElementById('sidebarOverlay').classList.contains('show')
        })"""
    )


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    page.goto(PAGE)
    page.wait_for_timeout(500)
    print("初始           :", state(page))

    # 1) 打开导航
    page.click("#sidebarToggle")
    page.wait_for_timeout(300)
    s1 = state(page)
    print("点导航按钮后   :", s1)

    # 2) 选一个单元 -> 应自动收起
    page.click('.unit-item[data-uid="c2u3"]')
    page.wait_for_timeout(300)
    s2 = state(page)
    heading = page.inner_text(".unit-content h2")
    print("选单元后       :", s2, "| heading =", heading.strip())

    # 3) 再打开 -> 点遮罩 -> 应关闭
    page.click("#sidebarToggle")
    page.wait_for_timeout(300)
    s3 = state(page)
    page.click("#sidebarOverlay", position={"x": 350, "y": 700})
    page.wait_for_timeout(300)
    s4 = state(page)
    print("再打开         :", s3)
    print("点遮罩后       :", s4)

    # 4) 桌面视口：不应出现 open/overlay 残留，且单元照常渲染
    ctx2 = browser.new_context(viewport={"width": 1440, "height": 900})
    page2 = ctx2.new_page()
    page2.on("pageerror", lambda e: errors.append(str(e)))
    page2.goto(PAGE)
    page2.wait_for_timeout(500)
    page2.click('.unit-item[data-uid="c4u2"]')
    page2.wait_for_timeout(300)
    s5 = state(page2)
    heading2 = page2.inner_text(".unit-content h2")
    print("桌面点单元后   :", s5, "| heading =", heading2.strip())

    browser.close()

print("errors:", errors if errors else "none")
ok = (
    s1["open"] and s1["overlay"]
    and not s2["open"] and not s2["overlay"]
    and "GELATERIA" in heading
    and s3["open"]
    and not s4["open"] and not s4["overlay"]
    and not s5["open"] and not s5["overlay"]
    and "ALBERGO" in heading2
    and not errors
)
print("SMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
