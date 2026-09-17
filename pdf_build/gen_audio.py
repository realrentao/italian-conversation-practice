# -*- coding: utf-8 -*-
"""
Batch-generate Italian TTS audio for the PDF-derived site.

Outputs (relative to BASE):
  audio/w/<sha1_12>.mp3                  keywords,  normal speed
  audio/s/<uid>_<idx>_<s|m|f>.mp3        common phrases, 3 speeds
  audio/d/<uid>_<seg>_<s|m|f>.mp3        video text, 3 speeds

Resumable: existing non-empty files are skipped.
Patches edge-tts's hard-coded xml:lang='en-US' -> 'it-IT' so Italian
is pronounced with Italian phonetics instead of English defaults.
"""
import asyncio, hashlib, json, os, re, sys, time
import edge_tts
import edge_tts.communicate as _C

# ---------- monkey-patch: xml:lang en-US -> it-IT ----------
_orig_mkssml = _C.mkssml


def _mkssml_it(tc, escaped_text):
    if isinstance(escaped_text, bytes):
        escaped_text = escaped_text.decode("utf-8")
    return (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='it-IT'>"
        f"<voice name='{tc.voice}'>"
        f"<prosody pitch='{tc.pitch}' rate='{tc.rate}' volume='{tc.volume}'>"
        f"{escaped_text}"
        "</prosody>"
        "</voice>"
        "</speak>"
    )


_C.mkssml = _mkssml_it

# ---------- config ----------
BASE = r"D:\意大利语材料\实用意大利语会话"
DATA = os.path.join(BASE, "pdf_build", "units_data.json")
VOICE = "it-IT-ElsaNeural"
RATES = {"s": "-30%", "m": "+0%", "f": "+25%"}
CONCURRENCY = 8
MAX_RETRY = 3

# ---------- text cleanup ----------
BULLET_RE = re.compile(r"^[\s•·▪◦‣※\-–—\*]+")


def clean(t):
    if not t:
        return ""
    s = str(t).replace("**", "").replace("〔?〕", "")
    s = s.replace("\u00a0", " ")
    lines = [BULLET_RE.sub("", ln).strip() for ln in s.split("\n")]
    s = " ".join(x for x in lines if x)
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def wpath(word):
    h = hashlib.sha1(word.strip().encode("utf-8")).hexdigest()[:12]
    return os.path.join("audio", "w", h + ".mp3")


# ---------- build task list ----------
def build_tasks():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    tasks = []  # (text, relpath, rate)
    seen = set()

    for c in data["chapters"]:
        for u in c["units"]:
            uid = u["id"]
            # keywords: one file per unique word, normal speed
            for v in u.get("vocab", []):
                txt = clean(v.get("it"))
                if not txt:
                    continue
                rel = wpath(txt)
                key = rel
                if key in seen:
                    continue
                seen.add(key)
                tasks.append((txt, rel, RATES["m"]))
            # common phrases: 3 speeds
            for i, s in enumerate(u.get("sentences", [])):
                txt = clean(s.get("it"))
                if not txt:
                    continue
                for sp, rt in RATES.items():
                    tasks.append(
                        (txt, os.path.join("audio", "s", f"{uid}_{i}_{sp}.mp3"), rt)
                    )
            # video text: 3 speeds
            for i, d in enumerate(u.get("dialogue", [])):
                txt = clean(d.get("it"))
                if not txt:
                    continue
                for sp, rt in RATES.items():
                    tasks.append(
                        (txt, os.path.join("audio", "d", f"{uid}_{i}_{sp}.mp3"), rt)
                    )
    return tasks


# ---------- worker ----------
DONE = {"ok": 0, "skip": 0, "fail": 0, "empty": 0}


async def synth(sem, text, rel, rate):
    out = os.path.join(BASE, rel)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        DONE["skip"] += 1
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".part"
    for attempt in range(1, MAX_RETRY + 1):
        try:
            async with sem:
                comm = edge_tts.Communicate(text, VOICE, rate=rate)
                with open(tmp, "wb") as f:
                    async for chunk in comm.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
            if os.path.getsize(tmp) > 0:
                os.replace(tmp, out)
                DONE["ok"] += 1
                return
            raise RuntimeError("empty output")
        except Exception as e:
            if attempt >= MAX_RETRY:
                DONE["fail"] += 1
                print(f"[FAIL] {rel} :: {e}", flush=True)
                try:
                    if os.path.exists(tmp):
                        os.remove(tmp)
                except OSError:
                    pass
                return
            await asyncio.sleep(1.2 * attempt)


async def main():
    tasks = build_tasks()
    total = len(tasks)
    print(f"[INFO] tasks={total} voice={VOICE}", flush=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    t0 = time.time()
    # run in slices for progress reporting
    SLICE = 100
    for start in range(0, total, SLICE):
        batch = tasks[start : start + SLICE]
        await asyncio.gather(*(synth(sem, t, r, rt) for (t, r, rt) in batch))
        el = time.time() - t0
        print(
            f"[PROG] {min(start+SLICE,total)}/{total} "
            f"ok={DONE['ok']} skip={DONE['skip']} fail={DONE['fail']} "
            f"({el:.0f}s)",
            flush=True,
        )
    print(
        f"[DONE] total={total} ok={DONE['ok']} skip={DONE['skip']} fail={DONE['fail']} "
        f"time={time.time()-t0:.0f}s",
        flush=True,
    )


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
