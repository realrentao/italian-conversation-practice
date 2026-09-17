# -*- coding: utf-8 -*-
"""Verify every audio path referenced by the rendered page exists on disk."""
import hashlib, json, os, sys

BASE = r"D:\意大利语材料\实用意大利语会话"
DATA = os.path.join(BASE, "pdf_build", "units_data.json")
HTML = os.path.join(BASE, "index.html")
MIN_BYTES = 1000

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

expected = []
for c in data["chapters"]:
    for u in c["units"]:
        uid = u["id"]
        for v in u.get("vocab", []):
            h = hashlib.sha1(v["it"].strip().encode("utf-8")).hexdigest()[:12]
            expected.append(os.path.join("audio", "w", h + ".mp3"))
        for i in range(len(u.get("sentences", []))):
            for sp in ("s", "m", "f"):
                expected.append(os.path.join("audio", "s", f"{uid}_{i}_{sp}.mp3"))
        for i in range(len(u.get("dialogue", []))):
            for sp in ("s", "m", "f"):
                expected.append(os.path.join("audio", "d", f"{uid}_{i}_{sp}.mp3"))

expected = sorted(set(expected))
missing, tiny, ok = [], [], 0
for rel in expected:
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        missing.append(rel)
    elif os.path.getsize(p) < MIN_BYTES:
        tiny.append((rel, os.path.getsize(p)))
    else:
        ok += 1

print(f"expected={len(expected)} ok={ok} missing={len(missing)} tiny={len(tiny)}")
for m in missing[:20]:
    print("  MISSING:", m)
for t in tiny[:20]:
    print("  TINY:", t)
if missing or tiny:
    sys.exit(1)
print("ALL AUDIO PRESENT")
