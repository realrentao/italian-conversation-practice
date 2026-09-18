# -*- coding: utf-8 -*-
"""Smoke test: c1u1 shows the 4 replaced video-text segments and 25 notes."""
import pathlib, sys
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(r"D:\意大利语材料\实用意大利语会话\index.html").as_uri()
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    page.goto(PAGE)
    page.click('.unit-item[data-uid="c1u1"]')
    page.wait_for_timeout(500)

    titles = page.eval_on_selector_all(".section-title", "els=>els.map(e=>e.innerText.trim())")
    segs = page.eval_on_selector_all(".dialogue-seg .d-it", "els=>els.map(e=>e.innerText.trim().slice(0,60))")
    notes = page.eval_on_selector_all(".note-item .term", "els=>els.map(e=>e.innerText.trim())")
    print("titles:", titles)
    print("note count:", len(notes))
    print("note terms:", notes[:6], "...", notes[-3:])
    for i, s in enumerate(segs, 1):
        print(f"Testo {i} starts: {s.splitlines()[0][:55]}")

    browser.close()

print("errors:", errors if errors else "none")
ok = (
    len(segs) == 4
    and segs[0].startswith("Dove si trovano gli annunci di locazione?")
    and "Posso fare un sopralluogo?" in segs[1]
    and "Poi ci sono due camere da letto" in segs[2]
    and "Una curiosità" in segs[3]
    and len(notes) == 25
    and notes[2] == "la parte più bassa"          # was mis-parsed as 'da parte più bassa'
    and "in disordine" in notes                    # second group restored
    and "buona giornata" in notes
    and not errors
)
print("SMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
