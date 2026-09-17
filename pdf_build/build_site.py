# -*- coding: utf-8 -*-
import json, hashlib, os

BASE = r"D:\意大利语材料\实用意大利语会话"
DATA = os.path.join(BASE, "pdf_build", "units_data.json")
TPL  = os.path.join(BASE, "pdf_build", "index_template.html")
OUT  = os.path.join(BASE, "index.html")

with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

# assign per-word audio paths (deduped by sha1 of the italian word)
def wpath(word):
    h = hashlib.sha1(word.strip().encode("utf-8")).hexdigest()[:12]
    return f"audio/w/{h}.mp3"

for c in data["chapters"]:
    for u in c["units"]:
        for v in u.get("vocab", []):
            v["audio"] = wpath(v["it"])

json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
json_str = json_str.replace("</", "<\\/")  # guard against </script>

with open(TPL, encoding="utf-8") as f:
    tpl = f.read()

html = tpl.replace("__BOOKDATA__", json_str)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print("Wrote", OUT, "size(KB)=", round(os.path.getsize(OUT)/1024, 1))
print("units:", sum(len(c["units"]) for c in data["chapters"]))
